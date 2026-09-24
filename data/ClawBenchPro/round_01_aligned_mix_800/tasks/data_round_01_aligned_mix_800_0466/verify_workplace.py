import os
import sys
import json
import csv
import glob
from datetime import datetime

def load_report(workspace):
    report_path = os.path.join(workspace, "deliverables/final_report.json")
    if not os.path.exists(report_path):
        return None
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def calculate_ground_truth(workspace):
    # 1. Attendance
    attended_uids = {} # uid -> name
    scan_dir = os.path.join(workspace, "raw_records/attendance_scans")
    for log_file in glob.glob(os.path.join(scan_dir, "*.log")):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if "| SUCCESS |" in line:
                    parts = line.strip().split(" | ")
                    if len(parts) == 4:
                        uid, name = parts[2], parts[3]
                        attended_uids[uid] = name

    # 2. Consent (Temporal Logic)
    consent_dir = os.path.join(workspace, "raw_records/consent_webhooks")
    latest_consents = {} # uid -> (timestamp, status)
    for hook_file in glob.glob(os.path.join(consent_dir, "*.json")):
        with open(hook_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data.get("type") == "CONSENT_UPDATE":
                uid = data["user_id"]
                ts = datetime.fromisoformat(data["timestamp"])
                status = data.get("status")
                if uid not in latest_consents or ts > latest_consents[uid][0]:
                    latest_consents[uid] = (ts, status)
    
    signed_uids = {uid for uid, (ts, status) in latest_consents.items() if status == "SIGNED"}

    # 3. Intersection
    cleared_names = sorted(list({attended_uids[uid] for uid in attended_uids if uid in signed_uids}))

    # 4. Finance
    eco_path = os.path.join(workspace, "raw_records/vendor_specs/eco_catalog.json")
    with open(eco_path, "r", encoding="utf-8") as f:
        eco_catalog = json.load(f)
    
    total_sustainable = 0.0
    finance_dir = os.path.join(workspace, "raw_records/finance")
    for csv_file in glob.glob(os.path.join(finance_dir, "*.csv")):
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["EventCode"] == "VS_2023":
                    item_id = row["ItemID"]
                    if eco_catalog.get(item_id, {}).get("is_sustainable"):
                        total_sustainable += int(row["Quantity"]) * float(row["UnitPrice"])

    return cleared_names, round(total_sustainable, 2)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. File existence and basic format
    report = load_report(workspace)
    if report:
        score += 10
        details.append({"item": "文件格式检查", "score": 10, "max_score": 10, "passed": True, "reason": "final_report.json 存在并可解析"})
    else:
        details.append({"item": "文件格式检查", "score": 0, "max_score": 10, "passed": False, "reason": "final_report.json 不存在或非合法JSON"})
        # 写入结果并退出
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 2. Key existence
    has_attendees = "cleared_attendees" in report
    has_expense = "total_sustainable_expense" in report
    if has_attendees and has_expense:
        score += 10
        details.append({"item": "字段完整性检查", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有必要字段"})
    else:
        details.append({"item": "字段完整性检查", "score": 0, "max_score": 10, "passed": False, "reason": "缺少必要字段"})

    # 3. Logic Validation
    truth_names, truth_expense = calculate_ground_truth(workspace)

    # 3.1 Attendees Validation (40 points)
    if has_attendees:
        agent_names = report["cleared_attendees"]
        if not isinstance(agent_names, list):
            details.append({"item": "参会名单格式", "score": 0, "max_score": 40, "passed": False, "reason": "cleared_attendees 不是列表"})
        else:
            # Check sorting
            is_sorted = agent_names == sorted(agent_names)
            # Check content
            correct_set = set(truth_names)
            agent_set = set(agent_names)
            
            intersection = correct_set.intersection(agent_set)
            if agent_set == correct_set:
                sub_score = 30 + (10 if is_sorted else 0)
                score += sub_score
                details.append({"item": "参会名单内容及排序", "score": sub_score, "max_score": 40, "passed": True, "reason": f"名单准确. 排序: {is_sorted}"})
            else:
                missing = correct_set - agent_set
                extra = agent_set - correct_set
                details.append({"item": "参会名单内容", "score": 0, "max_score": 40, "passed": False, "reason": f"名单不一致. 缺失: {list(missing)[:3]}, 多余: {list(extra)[:3]}"})

    # 3.2 Finance Validation (40 points)
    if has_expense:
        agent_val = report["total_sustainable_expense"]
        try:
            agent_val_f = float(agent_val)
            if abs(agent_val_f - truth_expense) < 0.01:
                score += 40
                details.append({"item": "可持续支出计算", "score": 40, "max_score": 40, "passed": True, "reason": f"计算结果 {agent_val_f} 与参考值一致"})
            else:
                details.append({"item": "可持续支出计算", "score": 0, "max_score": 40, "passed": False, "reason": f"计算错误. 预期 {truth_expense}, 得到 {agent_val_f}"})
        except:
            details.append({"item": "可持续支出计算", "score": 0, "max_score": 40, "passed": False, "reason": "金额无法解析为数值"})

    # Output score
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(score), "details": details}, f)

if __name__ == "__main__":
    verify()
