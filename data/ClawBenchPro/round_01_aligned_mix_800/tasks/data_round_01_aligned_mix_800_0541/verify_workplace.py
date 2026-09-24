import os
import sys
import json
import csv
import glob

def load_ground_truth(workspace):
    """
    通过模拟 env_builder 的逻辑，在评测脚本内部重新扫描一遍环境以获取绝对准确的期望值。
    这种方式可以应对随机生成的环境数据。
    """
    approved_rates = {}
    vault_path = os.path.join(workspace, "legacy_vault/contracts_v4_final/archives")
    for fragment in glob.glob(os.path.join(vault_path, "*.json")):
        with open(fragment, 'r') as f:
            data = json.load(f)
            approved_rates[data['entity']] = data['contract_terms']['hourly_fixed']
    
    expected_payouts = {name: 0.0 for name in approved_rates}
    overbillers = set()
    
    logs_path = os.path.join(workspace, "work_logs")
    for filename in os.listdir(logs_path):
        filepath = os.path.join(logs_path, filename)
        is_final = False
        contractor = None
        hours = 0
        claimed_rate = 0.0
        
        try:
            if filename.endswith(".csv"):
                with open(filepath, 'r', newline='') as f:
                    reader = list(csv.reader(f))
                    if len(reader) < 2: continue
                    # Header: Metadata_Status, Worker, Hours, Rate_Claimed
                    if reader[1][0] == "FINAL":
                        is_final = True
                        contractor = reader[1][1]
                        hours = float(reader[1][2])
                        claimed_rate = float(reader[1][3])
            elif filename.endswith(".json"):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if data.get("status") == "FINAL":
                        is_final = True
                        contractor = data.get("sub")
                        hours = float(data.get("duration"))
                        claimed_rate = float(data.get("rate"))
            else: # .log or .txt
                with open(filepath, 'r') as f:
                    content = f.read()
                    if "STATUS: FINAL" in content:
                        is_final = True
                        for line in content.splitlines():
                            if "CONTRACTOR:" in line: contractor = line.split(":")[1].strip()
                            if "HOURS_WORKED:" in line: hours = float(line.split(":")[1].strip())
                            if "CLAIMED_RATE:" in line: claimed_rate = float(line.split(":")[1].strip())
            
            if is_final and contractor in approved_rates:
                expected_payouts[contractor] += hours * approved_rates[contractor]
                if claimed_rate > approved_rates[contractor]:
                    overbillers.add(contractor)
        except Exception:
            continue
            
    return expected_payouts, overbillers

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "financial_reports")
    json_path = os.path.join(report_dir, "reconciliation_export.json")
    txt_path = os.path.join(report_dir, "flagged_contractors.txt")
    
    score_details = []
    total_score = 0
    
    # 1. 基础目录与文件存在检查 (10分)
    dir_exists = os.path.isdir(report_dir)
    json_exists = os.path.isfile(json_path)
    txt_exists = os.path.isfile(txt_path)
    
    step1_score = (5 if dir_exists else 0) + (2.5 if json_exists else 0) + (2.5 if txt_exists else 0)
    score_details.append({"item": "基础文件结构检查", "score": step1_score, "max_score": 10, "passed": step1_score == 10, "reason": f"Dir: {dir_exists}, JSON: {json_exists}, TXT: {txt_exists}"})
    total_score += step1_score

    if not (json_exists and txt_exists):
        # 核心文件缺失直接结算
        finalize(total_score, score_details)
        return

    # 获取真值
    gt_payouts, gt_overbillers = load_ground_truth(workspace)

    # 2. 验证 reconciliation_export.json (50分)
    try:
        with open(json_path, 'r') as f:
            agent_payouts = json.load(f)
        
        # 检查是否包含所有承包商且数值准确
        correct_payouts = 0
        total_contractors = len(gt_payouts)
        for name, gt_val in gt_payouts.items():
            if name in agent_payouts:
                # 允许 0.01 的浮点误差
                if abs(float(agent_payouts[name]) - gt_val) < 0.01:
                    correct_payouts += 1
        
        payout_score = int((correct_payouts / total_contractors) * 50)
        score_details.append({"item": "结算金额准确性 (JSON)", "score": payout_score, "max_score": 50, "passed": payout_score == 50, "reason": f"正确匹配 {correct_payouts}/{total_contractors} 个承包商金额"})
        total_score += payout_score
    except Exception as e:
        score_details.append({"item": "JSON 解析失败", "score": 0, "max_score": 50, "passed": False, "reason": str(e)})

    # 3. 验证 flagged_contractors.txt (40分)
    try:
        with open(txt_path, 'r') as f:
            agent_flagged = set(line.strip() for line in f if line.strip())
        
        # 计算交集、误报、漏报
        true_positives = agent_flagged.intersection(gt_overbillers)
        false_positives = agent_flagged - gt_overbillers
        false_negatives = gt_overbillers - agent_flagged
        
        if len(gt_overbillers) == 0:
            flag_score = 40 if len(agent_flagged) == 0 else 0
        else:
            # 基础分：召回率。惩罚分：误报。
            recall = len(true_positives) / len(gt_overbillers)
            base_flag_score = recall * 40
            # 每多出一个误报扣 10 分，扣完为止
            penalty = len(false_positives) * 10
            flag_score = max(0, int(base_flag_score - penalty))
            
        score_details.append({
            "item": "欺诈者识别准确性 (TXT)", 
            "score": flag_score, 
            "max_score": 40, 
            "passed": flag_score == 40, 
            "reason": f"准确识别: {len(true_positives)}, 漏报: {len(false_negatives)}, 误报: {len(false_positives)}"
        })
        total_score += flag_score
    except Exception as e:
        score_details.append({"item": "TXT 解析失败", "score": 0, "max_score": 40, "passed": False, "reason": str(e)})

    finalize(total_score, score_details)

def finalize(total_score, details):
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(total_score), "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
