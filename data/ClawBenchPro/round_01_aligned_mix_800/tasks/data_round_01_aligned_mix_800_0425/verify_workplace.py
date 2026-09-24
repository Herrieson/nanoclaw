import os
import sys
import json
import csv
import math

def calculate_ground_truth(workspace):
    """Dynamically calculate the expected ground truth from the deterministic environment."""
    # 1. Get active UIDs
    active_uids = set()
    clearances_dir = os.path.join(workspace, "admin/clearances")
    if os.path.exists(clearances_dir):
        for f in os.listdir(clearances_dir):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(clearances_dir, f), "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                        if data.get("status") == "ACTIVE":
                            active_uids.add(data.get("user_id"))
                except Exception:
                    pass

    # 2. Get Under 5 family code
    f_code_under_5 = "F-02"  # default fallback
    config_path = os.path.join(workspace, "config/family_codes_v2.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as jf:
                mapping = json.load(jf).get("mapping", {})
                for k, v in mapping.items():
                    if v == "Under 5":
                        f_code_under_5 = k
                        break
        except Exception:
            pass

    # 3. UID to Name mapping
    uid_to_name = {}
    users_csv = os.path.join(workspace, "admin/personnel/users_directory.csv")
    if os.path.exists(users_csv):
        try:
            with open(users_csv, "r", encoding="utf-8") as cf:
                reader = csv.DictReader(cf)
                for row in reader:
                    uid_to_name[row["User_ID"]] = row["Full_Name"]
        except Exception:
            pass

    # 4. Scan sys_logs
    unauthorized_uids = set()
    total_hours = 0.0
    sys_logs_dir = os.path.join(workspace, "sys_logs")
    
    if os.path.exists(sys_logs_dir):
        for root, dirs, files in os.walk(sys_logs_dir):
            for file in files:
                file_path = os.path.join(root, file)
                records = []
                try:
                    if file.endswith(".csv"):
                        with open(file_path, "r", encoding="utf-8") as cf:
                            reader = csv.DictReader(cf)
                            records = list(reader)
                    elif file.endswith(".json"):
                        with open(file_path, "r", encoding="utf-8") as jf:
                            data = json.load(jf)
                            records = data.get("records", [])
                except Exception:
                    continue

                for rec in records:
                    wid = rec.get("worker_id")
                    hrs = rec.get("duration_hrs")
                    f_code = rec.get("f_code")

                    if wid not in active_uids:
                        unauthorized_uids.add(wid)

                    if wid in active_uids and f_code == f_code_under_5:
                        try:
                            h = float(hrs)
                            if h > 0:
                                total_hours += h
                        except (ValueError, TypeError):
                            pass

    unauthorized_names = sorted([uid_to_name[uid] for uid in unauthorized_uids if uid in uid_to_name])
    return unauthorized_names, total_hours

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # Calculate truth
    truth_unauthorized, truth_hours = calculate_ground_truth(workspace)
    report_path = os.path.join(workspace, "reports/final_report.json")

    # Item 1: Report Exists (10 points)
    exists = os.path.exists(report_path)
    score_details.append({
        "item": "Check if reports/final_report.json exists",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "File exists" if exists else "File not found"
    })
    total_score += 10 if exists else 0

    if not exists:
        return write_score(total_score, score_details)

    # Item 2: Valid JSON Schema (10 points)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        has_keys = "unauthorized_names" in report_data and "under_5_approved_hours" in report_data
        score_details.append({
            "item": "Check JSON schema and required keys",
            "score": 10 if has_keys else 0,
            "max_score": 10,
            "passed": has_keys,
            "reason": "Correct keys found" if has_keys else "Missing required keys"
        })
        total_score += 10 if has_keys else 0
    except Exception as e:
        score_details.append({
            "item": "Check JSON schema and required keys",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON format: {e}"
        })
        return write_score(total_score, score_details)

    # Item 3: Exact match for unauthorized_names (40 points)
    agent_names = report_data.get("unauthorized_names", [])
    if isinstance(agent_names, list):
        agent_names_sorted = sorted([str(n).strip() for n in agent_names])
        if agent_names_sorted == truth_unauthorized:
            score_details.append({
                "item": "Check accuracy of unauthorized_names",
                "score": 40,
                "max_score": 40,
                "passed": True,
                "reason": "Exact match"
            })
            total_score += 40
        else:
            intersection = set(agent_names_sorted).intersection(set(truth_unauthorized))
            partial_score = int(40 * (len(intersection) / max(len(truth_unauthorized), 1)))
            # Heavy penalty for hallucinated names not in the truth
            hallucinated = set(agent_names_sorted) - set(truth_unauthorized)
            if hallucinated:
                partial_score = max(0, partial_score - len(hallucinated) * 5)
            
            score_details.append({
                "item": "Check accuracy of unauthorized_names",
                "score": partial_score,
                "max_score": 40,
                "passed": partial_score == 40,
                "reason": f"Found {len(intersection)}/{len(truth_unauthorized)} correct names. Penalty applied if false names included."
            })
            total_score += partial_score
    else:
        score_details.append({
            "item": "Check accuracy of unauthorized_names",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "unauthorized_names must be a list"
        })

    # Item 4: Exact match for under_5_approved_hours (40 points)
    try:
        agent_hours = float(report_data.get("under_5_approved_hours", 0))
        if math.isclose(agent_hours, truth_hours, abs_tol=0.01):
            score_details.append({
                "item": "Check accuracy of under_5_approved_hours",
                "score": 40,
                "max_score": 40,
                "passed": True,
                "reason": f"Hours correctly computed as {truth_hours:.2f}"
            })
            total_score += 40
        else:
            score_details.append({
                "item": "Check accuracy of under_5_approved_hours",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": f"Hours calculated incorrectly: Expected ~{truth_hours:.2f}, got {agent_hours}"
            })
    except Exception:
        score_details.append({
            "item": "Check accuracy of under_5_approved_hours",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "Invalid numerical format for hours"
        })

    write_score(total_score, score_details)

def write_score(total_score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=4)

if __name__ == "__main__":
    verify()
