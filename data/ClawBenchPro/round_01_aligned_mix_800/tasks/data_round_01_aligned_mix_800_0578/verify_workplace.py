import os
import sys
import json
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查目标文件是否存在
    target_path = os.path.join(workspace, "vault/compliance_final.json")
    if os.path.exists(target_path):
        score += 10
        details.append({"item": "Audit report exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found vault/compliance_final.json"})
    else:
        details.append({"item": "Audit report exists", "score": 0, "max_score": 10, "passed": False, "reason": "vault/compliance_final.json not found"})
        # 写入初步结果并退出，因为后续检查依赖此文件
        write_score(0, details)
        return

    # 2. 检查 JSON 格式合法性
    try:
        with open(target_path, 'r') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "Valid JSON format", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed successfully"})
    except Exception as e:
        details.append({"item": "Valid JSON format", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse JSON: {e}"})
        write_score(score, details)
        return

    # 3. 核心数据准确性检查 (Ground Truth)
    # Expected: 
    # DOC-SIGMA-92: 3 (CSV/P-1, JSON/P-4, TXT/P-7)
    # DOC-OMEGA-11: 1 (JSON/P-11) -> P-8 is redacted, P-2 has no SSN
    # DOC-EPSILON-04: 2 (TXT/P-6, JSON/P-10) -> P-5 has no SSN
    expected_results = {
        "DOC-SIGMA-92": 3,
        "DOC-OMEGA-11": 1,
        "DOC-EPSILON-04": 2
    }
    
    # 检查是否包含多余的非活动医生或退役医生
    all_keys = set(data.keys())
    active_keys = set(expected_results.keys())
    
    # A. 检查活动医生数据的准确性
    accuracy_points = 60
    per_doc_points = accuracy_points // len(expected_results)
    
    for doc_id, expected_count in expected_results.items():
        if doc_id in data:
            actual_count = data[doc_id]
            if actual_count == expected_count:
                score += per_doc_points
                details.append({"item": f"Data Accuracy: {doc_id}", "score": per_doc_points, "max_score": per_doc_points, "passed": True, "reason": f"Found {expected_count} violations"})
            else:
                details.append({"item": f"Data Accuracy: {doc_id}", "score": 0, "max_score": per_doc_points, "passed": False, "reason": f"Expected {expected_count}, but found {actual_count}"})
        else:
            details.append({"item": f"Data Accuracy: {doc_id}", "score": 0, "max_score": per_doc_points, "passed": False, "reason": "Doctor ID missing in report"})

    # B. 检查对无效数据的过滤 (Inactive staff, Temp files, Redacted)
    # 违规惩罚：如果出现了 DOC-OLD-01 或 DOC-VOID-99
    filtering_score = 20
    invalid_staff = ["DOC-OLD-01", "DOC-VOID-99"]
    found_invalid = [staff for staff in invalid_staff if staff in data and data[staff] > 0]
    
    # 检查是否有虚假的 Temp 文件数据（P-9 是 DECOY）
    # 如果 SIGMA 的数量是 4 而不是 3，说明它包含了 TEMP_LOG_99.csv 的数据
    contain_temp_data = (data.get("DOC-SIGMA-92", 0) > 3)
    
    if not found_invalid and not contain_temp_data:
        score += filtering_score
        details.append({"item": "Data Filtering Logic", "score": filtering_score, "max_score": filtering_score, "passed": True, "reason": "Successfully filtered inactive staff and temporary/decoy files."})
    else:
        reason = ""
        if found_invalid: reason += f"Included inactive staff: {found_invalid}. "
        if contain_temp_data: reason += "Failed to filter TEMP_LOG prefix files. "
        details.append({"item": "Data Filtering Logic", "score": 0, "max_score": filtering_score, "passed": False, "reason": reason.strip()})

    write_score(score, details)

def write_score(score, details):
    output = {
        "total_score": int(score),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    verify()
