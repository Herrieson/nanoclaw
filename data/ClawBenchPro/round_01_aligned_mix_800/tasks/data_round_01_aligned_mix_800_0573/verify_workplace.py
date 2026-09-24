import os
import sys
import json
import pandas as pd
import glob

def get_ground_truth(workspace):
    """
    根据任务逻辑在评测脚本中复刻计算逻辑，获取标准答案。
    """
    # 1. 获取白名单人员
    white_list_names = set()
    personnel_files = glob.glob(os.path.join(workspace, "archives/personnel/**/*.json"), recursive=True)
    for f_path in personnel_files:
        with open(f_path, 'r') as f:
            data = json.load(f)
            if data.get("department") == "Cross-Cultural Education" and data.get("status") == "active":
                white_list_names.add(data.get("name"))

    # 2. 获取有效产出项目
    valid_projects = set()
    pub_files = glob.glob(os.path.join(workspace, "archives/publications/**/*.json"), recursive=True)
    for f_path in pub_files:
        with open(f_path, 'r') as f:
            data = json.load(f)
            if data.get("review_status") == "approved" and data.get("publication_state") == "published":
                valid_projects.add(data.get("project_code"))

    # 3. 处理账单
    suspicious_ids = []
    total_suspicious_amount = 0.0
    
    ledger_files = glob.glob(os.path.join(workspace, "archives/finance/ledgers/**/*_certified.csv"), recursive=True)
    for f_path in ledger_files:
        df = pd.read_csv(f_path)
        for _, row in df.iterrows():
            # 清洗金额
            amt_str = str(row['amount']).replace("$", "").replace("USD", "").replace(",", "").strip()
            try:
                amt = float(amt_str)
            except:
                amt = 0.0
            
            is_suspicious = False
            # 规则1：人员不在白名单
            if row['faculty_name'] not in white_list_names:
                is_suspicious = True
            # 规则2：金额 > 5000 且 产出无效
            elif amt > 5000:
                if row['project_ref'] not in valid_projects:
                    is_suspicious = True
            
            if is_suspicious:
                suspicious_ids.append(row['txn_id'])
                total_suspicious_amount += amt
                
    return set(suspicious_ids), round(total_suspicious_amount, 2)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "investigation_report")
    suspicious_file = os.path.join(report_dir, "suspicious_list.json")
    summary_file = os.path.join(report_dir, "summary.json")
    
    score = 0
    details = []

    # 1. 基础文件存在性检查 (10分)
    if os.path.exists(suspicious_file) and os.path.exists(summary_file):
        score += 10
        details.append({"item": "Result files existence", "score": 10, "max_score": 10, "passed": True, "reason": "Both output files found."})
    else:
        details.append({"item": "Result files existence", "score": 0, "max_score": 10, "passed": False, "reason": "Missing suspicious_list.json or summary.json."})
        # 如果文件不存在，后续逻辑无法执行，直接写入结果
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 获取标准答案
    gt_ids, gt_amount = get_ground_truth(workspace)

    # 2. 验证 suspicious_list.json (40分)
    try:
        with open(suspicious_file, 'r') as f:
            agent_ids = set(json.load(f))
        
        # 计算交并比或准确率
        if agent_ids == gt_ids:
            score += 40
            details.append({"item": "Suspicious IDs Accuracy", "score": 40, "max_score": 40, "passed": True, "reason": "All suspicious transaction IDs match perfectly."})
        else:
            # 给出部分分：检查遗漏或多余
            missing = gt_ids - agent_ids
            extra = agent_ids - gt_ids
            correct_count = len(gt_ids & agent_ids)
            partial_score = max(0, int(40 * (correct_count / len(gt_ids)) - 5 * len(extra) / len(gt_ids)))
            score += partial_score
            details.append({"item": "Suspicious IDs Accuracy", "score": partial_score, "max_score": 40, "passed": False, "reason": f"Mismatch. Missing: {len(missing)}, Extra: {len(extra)}"})
    except Exception as e:
        details.append({"item": "Suspicious IDs Accuracy", "score": 0, "max_score": 40, "passed": False, "reason": f"JSON parse error: {str(e)}"})

    # 3. 验证 summary.json 字段与数值 (50分)
    try:
        with open(summary_file, 'r') as f:
            summary_data = json.load(f)
        
        item_score = 0
        # 3.1 数量检查 (20分)
        if summary_data.get("total_suspicious_count") == len(gt_ids):
            item_score += 20
            details.append({"item": "Summary Count", "score": 20, "max_score": 20, "passed": True, "reason": "Count matches."})
        else:
            details.append({"item": "Summary Count", "score": 0, "max_score": 20, "passed": False, "reason": f"Count mismatch. Expected {len(gt_ids)}, got {summary_data.get('total_suspicious_count')}"})
        
        # 3.2 金额检查 (30分)
        # 考虑到浮点数精度，允许 0.1 的误差
        agent_amt = summary_data.get("total_suspicious_amount", 0)
        if abs(agent_amt - gt_amount) < 0.1:
            item_score += 30
            details.append({"item": "Summary Amount", "score": 30, "max_score": 30, "passed": True, "reason": "Amount matches."})
        else:
            diff_ratio = abs(agent_amt - gt_amount) / (gt_amount + 1e-6)
            if diff_ratio < 0.05: # 5%以内给部分分
                item_score += 15
                details.append({"item": "Summary Amount", "score": 15, "max_score": 30, "passed": False, "reason": f"Amount close but slightly off. Expected {gt_amount}, got {agent_amt}"})
            else:
                details.append({"item": "Summary Amount", "score": 0, "max_score": 30, "passed": False, "reason": f"Amount mismatch. Expected {gt_amount}, got {agent_amt}"})
        
        score += item_score
    except Exception as e:
        details.append({"item": "Summary Logic", "score": 0, "max_score": 50, "passed": False, "reason": f"Error parsing summary: {str(e)}"})

    # 写入最终得分
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(score), "details": details}, f)

if __name__ == "__main__":
    verify()
