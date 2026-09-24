import os
import sys
import json
import csv

def generate_ground_truth(workspace):
    customers = {}
    csv_path = os.path.join(workspace, "db", "customers.csv")
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                customers[row["customer_id"]] = row["full_name"]
                
    vips = set()
    json_path = os.path.join(workspace, "db", "memberships.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            memberships = json.load(f)
            for m in memberships:
                if m.get("status") == "active" and m.get("level", 0) >= 4:
                    c_id = m.get("c_id")
                    if c_id in customers:
                        vips.add(customers[c_id])
                        
    vip_alerts = []
    junk_count = 0
    junk_keywords = {"none", "n/a", "unknown", "null", ""}
    
    week_42_dir = os.path.join(workspace, "logs", "week_42")
    if os.path.exists(week_42_dir):
        for fname in os.listdir(week_42_dir):
            if not fname.endswith(".txt"): continue
            with open(os.path.join(week_42_dir, fname), "r", encoding="utf-8") as f:
                for line in f:
                    if "[LOST & FOUND]" in line:
                        parts = line.split("ITEM: ")
                        if len(parts) > 1:
                            sub_parts = parts[1].split(" | OWNER: ")
                            if len(sub_parts) == 2:
                                item = sub_parts[0].strip()
                                owner = sub_parts[1].strip()
                                
                                if owner in vips:
                                    vip_alerts.append({"vip_name": owner, "item": item})
                                    
                                if owner.lower() in junk_keywords:
                                    junk_count += 1
                                    
    # Sort for deterministic comparison
    vip_alerts.sort(key=lambda x: (x["vip_name"], x["item"]))
    return vip_alerts, junk_count

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0
    
    # Generate Ground Truth
    try:
        gt_vip_alerts, gt_junk_count = generate_ground_truth(workspace)
    except Exception as e:
        print(f"Error generating ground truth: {e}")
        gt_vip_alerts, gt_junk_count = [], 0

    deliverables_dir = os.path.join(workspace, "deliverables")
    
    # 1. Check deliverables directory (10 pts)
    if os.path.isdir(deliverables_dir):
        total_score += 10
        details.append({"item": "Directory Check", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables/ directory exists."})
    else:
        details.append({"item": "Directory Check", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables/ directory does not exist."})

    # 2. Check junk_count.txt file and format (10 pts)
    junk_count_path = os.path.join(deliverables_dir, "junk_count.txt")
    agent_junk_count = None
    if os.path.isfile(junk_count_path):
        try:
            with open(junk_count_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                agent_junk_count = int(content)
            total_score += 10
            details.append({"item": "Junk Count File Format", "score": 10, "max_score": 10, "passed": True, "reason": "junk_count.txt exists and contains a valid integer."})
        except ValueError:
            details.append({"item": "Junk Count File Format", "score": 0, "max_score": 10, "passed": False, "reason": "junk_count.txt exists but does not contain a valid integer."})
    else:
        details.append({"item": "Junk Count File Format", "score": 0, "max_score": 10, "passed": False, "reason": "junk_count.txt does not exist."})

    # 3. Check junk count value (30 pts)
    if agent_junk_count is not None:
        if agent_junk_count == gt_junk_count:
            total_score += 30
            details.append({"item": "Junk Count Accuracy", "score": 30, "max_score": 30, "passed": True, "reason": f"Correct junk count: {agent_junk_count}."})
        else:
            details.append({"item": "Junk Count Accuracy", "score": 0, "max_score": 30, "passed": False, "reason": f"Expected {gt_junk_count}, but got {agent_junk_count}."})
    else:
        details.append({"item": "Junk Count Accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "Junk count value not available."})

    # 4. Check vip_alerts.json file and format (10 pts)
    vip_alerts_path = os.path.join(deliverables_dir, "vip_alerts.json")
    agent_vip_alerts = None
    if os.path.isfile(vip_alerts_path):
        try:
            with open(vip_alerts_path, "r", encoding="utf-8") as f:
                agent_vip_alerts = json.load(f)
            if isinstance(agent_vip_alerts, list) and all(isinstance(x, dict) and "vip_name" in x and "item" in x for x in agent_vip_alerts):
                total_score += 10
                details.append({"item": "VIP Alerts JSON Format", "score": 10, "max_score": 10, "passed": True, "reason": "vip_alerts.json exists and has correct list-of-dicts schema."})
            else:
                details.append({"item": "VIP Alerts JSON Format", "score": 0, "max_score": 10, "passed": False, "reason": "vip_alerts.json schema invalid. Must be a list of dicts with 'vip_name' and 'item'."})
                agent_vip_alerts = None
        except Exception as e:
            details.append({"item": "VIP Alerts JSON Format", "score": 0, "max_score": 10, "passed": False, "reason": f"vip_alerts.json failed to parse: {e}"})
    else:
        details.append({"item": "VIP Alerts JSON Format", "score": 0, "max_score": 10, "passed": False, "reason": "vip_alerts.json does not exist."})

    # 5. Check VIP alerts accuracy (40 pts)
    if agent_vip_alerts is not None:
        agent_vip_tuples = [(x["vip_name"], x["item"]) for x in agent_vip_alerts]
        gt_vip_tuples = [(x["vip_name"], x["item"]) for x in gt_vip_alerts]
        
        agent_set = set(agent_vip_tuples)
        gt_set = set(gt_vip_tuples)
        
        missing = gt_set - agent_set
        extra = agent_set - gt_set
        
        if len(missing) == 0 and len(extra) == 0 and len(agent_vip_tuples) == len(gt_vip_tuples):
            total_score += 40
            details.append({"item": "VIP Alerts Accuracy", "score": 40, "max_score": 40, "passed": True, "reason": "VIP alerts match ground truth perfectly."})
        else:
            partial_score = max(0, 40 - len(missing) * 5 - len(extra) * 5 - (len(agent_vip_tuples) - len(agent_set)) * 5)
            total_score += partial_score
            details.append({"item": "VIP Alerts Accuracy", "score": partial_score, "max_score": 40, "passed": partial_score == 40, "reason": f"Mismatch found. Missing: {len(missing)}, Extra/Dupes: {len(extra) + (len(agent_vip_tuples) - len(agent_set))}."})
    else:
        details.append({"item": "VIP Alerts Accuracy", "score": 0, "max_score": 40, "passed": False, "reason": "Valid VIP alerts data not available for verification."})

    score_data = {
        "total_score": total_score,
        "details": details
    }

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    verify()
