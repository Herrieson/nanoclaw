import os
import sys
import json
import glob

def load_catalog(workspace):
    """构建完整的资产分类映射"""
    catalog_path = os.path.join(workspace, "archive/system/config/assets")
    full_catalog = {}
    if os.path.exists(catalog_path):
        for part in ["part_alpha.json", "part_omega.json"]:
            p = os.path.join(catalog_path, part)
            if os.path.exists(p):
                with open(p, 'r') as f:
                    full_catalog.update(json.load(f))
    return full_catalog

def calculate_ground_truth(workspace):
    """计算标准答案"""
    catalog = load_catalog(workspace)
    if not catalog:
        return None, None
    
    rep_stats = {} # {name: {"green": 0, "total": 0}}
    green_contracts = []
    
    # 遍历日志
    log_pattern = os.path.join(workspace, "archive/logs/node_*/*_final.log")
    for log_file in glob.glob(log_pattern):
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if not lines or "TIMESTAMP|CONTRACT_ID|REP|ASSET_ID" not in lines[0]:
                continue
            
            for line in lines[1:]:
                parts = line.strip().split('|')
                if len(parts) != 4: continue
                _, cid, rep, aid = parts
                
                if rep not in rep_stats:
                    rep_stats[rep] = {"green": 0, "total": 0}
                
                rep_stats[rep]["total"] += 1
                asset_info = catalog.get(aid, {})
                if asset_info.get("category") == "Green":
                    rep_stats[rep]["green"] += 1
                    green_contracts.append(cid)

    # 检查合规性
    missing_compliance = []
    cert_dir = os.path.join(workspace, "archive/vault/legal/compliance/certificates")
    for cid in green_contracts:
        cert_path = os.path.join(cert_dir, f"{cid}_signed.txt")
        if not os.path.exists(cert_path):
            missing_compliance.append(cid)
            
    # 格式化 rep_stats 为最终对比格式
    final_stats = {}
    for rep, data in rep_stats.items():
        ratio = round(data["green"] / data["total"], 2) if data["total"] > 0 else 0.0
        final_stats[rep] = {"green_count": data["green"], "green_ratio": ratio}
        
    return final_stats, sorted(list(set(missing_compliance)))

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = os.path.join(workspace, "deliverables/audit_summary.json")
    score_file = "workplace_score.json"
    
    score = 0
    details = []

    # 1. 检查结果文件是否存在 (10分)
    if os.path.exists(output_file):
        score += 10
        details.append({"item": "File existence", "score": 10, "max_score": 10, "passed": True, "reason": "audit_summary.json found"})
        
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            gt_stats, gt_missing = calculate_ground_truth(workspace)
            
            # 2. 检查销售统计数据 (45分)
            if "rep_stats" in data:
                correct_reps = 0
                total_reps = len(gt_stats)
                for rep, stats in gt_stats.items():
                    if rep in data["rep_stats"]:
                        agent_s = data["rep_stats"][rep]
                        # 允许比例有 0.01 的浮点误差
                        if agent_s.get("green_count") == stats["green_count"] and \
                           abs(agent_s.get("green_ratio", 0) - stats["green_ratio"]) <= 0.01:
                            correct_reps += 1
                
                rep_score = int((correct_reps / total_reps) * 45) if total_reps > 0 else 0
                score += rep_score
                details.append({"item": "Rep Statistics Accuracy", "score": rep_score, "max_score": 45, "passed": rep_score == 45, 
                                "reason": f"Correctly calculated stats for {correct_reps}/{total_reps} reps"})
            else:
                details.append({"item": "Rep Statistics Accuracy", "score": 0, "max_score": 45, "passed": False, "reason": "rep_stats key missing"})

            # 3. 检查缺失合规项 (45分)
            if "missing_compliance" in data:
                agent_missing = sorted(data["missing_compliance"])
                if agent_missing == gt_missing:
                    score += 45
                    details.append({"item": "Missing Compliance List", "score": 45, "max_score": 45, "passed": True, "reason": "Missing contract IDs match ground truth exactly"})
                else:
                    # 部分得分逻辑：交集/并集
                    intersection = set(agent_missing).intersection(set(gt_missing))
                    partial = int((len(intersection) / max(len(gt_missing), len(agent_missing), 1)) * 45)
                    score += partial
                    details.append({"item": "Missing Compliance List", "score": partial, "max_score": 45, "passed": False, 
                                    "reason": f"Mismatched list. Found {len(intersection)} correct out of {len(gt_missing)} expected."})
            else:
                details.append({"item": "Missing Compliance List", "score": 0, "max_score": 45, "passed": False, "reason": "missing_compliance key missing"})

        except Exception as e:
            details.append({"item": "JSON Parsing", "score": 0, "max_score": 90, "passed": False, "reason": f"Error parsing JSON: {str(e)}"})
    else:
        details.append({"item": "File existence", "score": 0, "max_score": 100, "passed": False, "reason": "audit_summary.json not found in deliverables/"})

    result = {"total_score": score, "details": details}
    with open(score_file, 'w') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
