import os
import sys
import json
import yaml
import glob

def verify_audit_report(workspace):
    score = 0
    details = []
    report_path = os.path.join(workspace, "deliverables/audit_report.json")
    
    # 1. 检查文件是否存在 (10分)
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "Audit report exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found audit_report.json"})
    else:
        details.append({"item": "Audit report exists", "score": 0, "max_score": 10, "passed": False, "reason": "audit_report.json not found"})
        # 如果文件不存在，后续检查无法进行，直接输出
        return score, details

    # 2. 解析文件内容与 Schema 合法性 (10分)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        score += 10
        details.append({"item": "JSON Schema Validity", "score": 10, "max_score": 10, "passed": True, "reason": "Successfully parsed JSON"})
    except Exception as e:
        details.append({"item": "JSON Schema Validity", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse JSON: {e}"})
        return score, details

    # 3. 验证冒牌货 ID 列表 (40分)
    # 根据 Idea：imposters 为 ["BAD-666", "GHOST-00", "TRICK-99"]
    expected_imposters = ["BAD-666", "GHOST-00", "TRICK-99"]
    actual_imposters = data.get("imposter_ids", data.get("imposters", [])) # 兼容可能的 key 名
    
    if not isinstance(actual_imposters, list):
        details.append({"item": "Imposter ID format", "score": 0, "max_score": 40, "passed": False, "reason": "imposter_ids should be a list"})
    else:
        # 检查是否包含所有正确的 ID 且没有多余的 (30分)
        correct_set = set(expected_imposters)
        actual_set = set(actual_imposters)
        
        if actual_set == correct_set:
            score += 30
            # 检查排序 (额外 10分)
            if actual_imposters == expected_imposters:
                score += 10
                details.append({"item": "Imposter IDs accuracy & sorting", "score": 40, "max_score": 40, "passed": True, "reason": "All imposter IDs found and correctly sorted"})
            else:
                details.append({"item": "Imposter IDs accuracy & sorting", "score": 30, "max_score": 40, "passed": False, "reason": "IDs are correct but not sorted alphabetically"})
        else:
            details.append({"item": "Imposter IDs accuracy", "score": 0, "max_score": 40, "passed": False, "reason": f"Expected {expected_imposters}, got {actual_imposters}"})

    # 4. 验证合规开销总额 (40分)
    # 根据 Idea：150.75 + 45.00 + 88.25 + 320.00 = 604.00
    expected_total = 604.00
    actual_total = data.get("total_eligible_expenses", data.get("total_amount", data.get("compliant_total", 0)))
    
    try:
        actual_total_float = float(actual_total)
        if abs(actual_total_float - expected_total) < 0.01:
            score += 40
            details.append({"item": "Total expense calculation", "score": 40, "max_score": 40, "passed": True, "reason": f"Total correctly calculated as {expected_total}"})
        else:
            # 给出部分分数：如果 Agent 错误地包含了不合规类别（如 Travel）或读取了错误的 Policy
            details.append({"item": "Total expense calculation", "score": 0, "max_score": 40, "passed": False, "reason": f"Expected {expected_total}, but got {actual_total_float}"})
    except:
        details.append({"item": "Total expense calculation", "score": 0, "max_score": 40, "passed": False, "reason": "Could not parse total amount as a number"})

    return score, details

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score, score_details = verify_audit_report(workspace_dir)
    
    output = {
        "total_score": int(total_score),
        "details": score_details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
