import os
import sys
import json
import csv
import math

def calculate_ground_truth(workspace):
    catalog_path = os.path.join(workspace, "inventory_master", "item_catalog.json")
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    v2_codes_path = os.path.join(workspace, "guidelines", "status_codes_v2.csv")
    valid_codes = set()
    with open(v2_codes_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Usable", "").strip().lower() == "true":
                valid_codes.add(row["Code"])

    inventory = {name: 0 for name in catalog.values()}
    
    donations_dir = os.path.join(workspace, "donations")
    for root, _, files in os.walk(donations_dir):
        for file in files:
            file_lower = file.lower()
            if "draft" in file_lower or file_lower.endswith(".bak"):
                continue
            
            filepath = os.path.join(root, file)
            if file_lower.endswith(".json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        for r in data:
                            if r.get("status_code") in valid_codes:
                                item_name = catalog.get(r.get("item_id"))
                                if item_name:
                                    inventory[item_name] += int(r.get("qty", 0))
                    except Exception:
                        pass
            elif file_lower.endswith(".csv"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        reader = csv.DictReader(f)
                        for r in reader:
                            if r.get("status_code") in valid_codes:
                                item_name = catalog.get(r.get("item_id"))
                                if item_name:
                                    inventory[item_name] += int(r.get("qty", 0))
                    except Exception:
                        pass

    requests = {}
    req_dir = os.path.join(workspace, "family_requests")
    for root, _, files in os.walk(req_dir):
        for file in files:
            if file.endswith(".txt"):
                filepath = os.path.join(root, file)
                fam_id = None
                needs = {}
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    in_needs = False
                    for line in lines:
                        line = line.strip()
                        if line.startswith("Family ID:"):
                            fam_id = line.split(":", 1)[1].strip()
                        elif line == "Needs:":
                            in_needs = True
                        elif in_needs and line.startswith("-"):
                            parts = line[1:].split(":")
                            if len(parts) == 2:
                                item_name = parts[0].strip()
                                qty = int(parts[1].strip())
                                needs[item_name] = qty
                        elif in_needs and not line.startswith("-") and line != "":
                            in_needs = False
                if fam_id:
                    requests[fam_id] = needs

    allocations = {}
    shortages = {name: 0 for name in catalog.values()}

    for fam_id in sorted(requests.keys()):
        fam_alloc = {}
        for item, req_qty in requests[fam_id].items():
            avail = inventory.get(item, 0)
            allocated = min(req_qty, avail)
            if allocated > 0:
                fam_alloc[item] = allocated
                inventory[item] -= allocated
            
            short = req_qty - allocated
            if short > 0:
                shortages[item] += short
        if fam_alloc:
            allocations[fam_id] = fam_alloc

    final_shortages = {k: v for k, v in shortages.items() if v > 0}
    
    return allocations, final_shortages

def evaluate(workspace):
    results = []
    total_score = 0
    
    gt_allocations, gt_shortages = calculate_ground_truth(workspace)
    
    plan_path = os.path.join(workspace, "outreach_plan", "final_plan.json")
    
    if not os.path.exists(plan_path):
        results.append({
            "item": "Check if output file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File outreach_plan/final_plan.json does not exist."
        })
        return 0, results
    
    results.append({
        "item": "Check if output file exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "outreach_plan/final_plan.json exists."
    })
    total_score += 10
    
    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            agent_data = json.load(f)
    except Exception as e:
        results.append({
            "item": "Valid JSON format",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"File is not a valid JSON: {e}"
        })
        return total_score, results
        
    results.append({
        "item": "Valid JSON format",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "JSON parsed successfully."
    })
    total_score += 10
    
    agent_alloc = agent_data.get("allocations", {})
    agent_short = agent_data.get("shortages", {})
    
    # Evaluate Allocations
    alloc_max_score = 50
    gt_alloc_items = sum(len(items) for items in gt_allocations.values())
    agent_alloc_items = sum(len(items) if isinstance(items, dict) else 0 for items in agent_alloc.values() if isinstance(agent_alloc, dict))
    
    matched_alloc = 0
    penalty_alloc = 0
    if isinstance(agent_alloc, dict):
        for fam_id, items in agent_alloc.items():
            if fam_id not in gt_allocations:
                penalty_alloc += len(items) if isinstance(items, dict) else 1
                continue
            if isinstance(items, dict):
                for item, qty in items.items():
                    if item in gt_allocations[fam_id] and gt_allocations[fam_id][item] == qty:
                        matched_alloc += 1
                    else:
                        penalty_alloc += 1
    
    alloc_score = max(0, int((matched_alloc / max(1, gt_alloc_items)) * alloc_max_score) - penalty_alloc * 2)
    alloc_score = min(alloc_max_score, alloc_score)
    
    results.append({
        "item": "Accuracy of Allocations",
        "score": alloc_score,
        "max_score": alloc_max_score,
        "passed": alloc_score == alloc_max_score,
        "reason": f"Matched {matched_alloc}/{gt_alloc_items} allocation records. Penalties for hallucinated/wrong records: {penalty_alloc}."
    })
    total_score += alloc_score

    # Evaluate Shortages
    short_max_score = 30
    gt_short_items = len(gt_shortages)
    
    matched_short = 0
    penalty_short = 0
    if isinstance(agent_short, dict):
        for item, qty in agent_short.items():
            if item in gt_shortages and gt_shortages[item] == qty:
                matched_short += 1
            else:
                penalty_short += 1
                
    short_score = max(0, int((matched_short / max(1, gt_short_items)) * short_max_score) - penalty_short * 2)
    short_score = min(short_max_score, short_score)
    
    results.append({
        "item": "Accuracy of Shortages",
        "score": short_score,
        "max_score": short_max_score,
        "passed": short_score == short_max_score,
        "reason": f"Matched {matched_short}/{gt_short_items} shortage records. Penalties for hallucinated/wrong records: {penalty_short}."
    })
    total_score += short_score

    return total_score, results

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    final_score, eval_details = evaluate(workspace_dir)
    
    output = {
        "total_score": final_score,
        "details": eval_details
    }
    
    with open(os.path.join(workspace_dir, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)
