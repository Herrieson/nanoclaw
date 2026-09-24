import os
import sys
import json
import csv
import glob

def calculate_ground_truth(workspace):
    """
    Simulate the logic described in the task to get the correct values.
    This is necessary because the environment is randomized by env_builder.py.
    """
    archives_path = os.path.join(workspace, "pta_data_dump/archives")
    cancellations_path = os.path.join(workspace, "pta_data_dump/front_desk/cancellations.txt")
    parent_dir_path = os.path.join(workspace, "pta_data_dump/system_exports/parent_directory.json")
    
    # 1. Get cancelled transactions
    voided_ids = set()
    if os.path.exists(cancellations_path):
        with open(cancellations_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("TXN"):
                    voided_ids.add(line)
                    
    # 2. Get parent directory
    parent_map = {}
    if os.path.exists(parent_dir_path):
        with open(parent_dir_path, 'r') as f:
            data = json.load(f)
            for entry in data:
                parent_map[entry['parent_id']] = entry['full_name']

    # 3. Parse all transaction files
    children_book_count = 0
    # parent_id -> {'has_book': bool, 'has_bake': bool}
    parent_status = {}

    target_campaign = "St. Jude's Book & Bake"
    
    all_files = glob.glob(os.path.join(archives_path, "**/*_log.*"), recursive=True)
    
    for file_path in all_files:
        if file_path.endswith(".json"):
            try:
                with open(file_path, 'r') as f:
                    txn = json.load(f)
                    if txn['txn_id'] in voided_ids or txn['campaign'] != target_campaign:
                        continue
                    
                    p_id = txn['parent_id']
                    if p_id not in parent_status:
                        parent_status[p_id] = {'has_book': False, 'has_bake': False}
                    
                    for item in txn['items']:
                        if item['type'] == "ChildrensBook":
                            children_book_count += item['qty']
                            parent_status[p_id]['has_book'] = True
                        elif item['type'] == "AdultBook":
                            parent_status[p_id]['has_book'] = True
                        elif item['type'] == "BakedGood":
                            parent_status[p_id]['has_bake'] = True
            except: continue
            
        elif file_path.endswith(".csv"):
            try:
                with open(file_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['txn_id'] in voided_ids or row['campaign'] != target_campaign:
                            continue
                        
                        p_id = row['parent_id']
                        if p_id not in parent_status:
                            parent_status[p_id] = {'has_book': False, 'has_bake': False}
                        
                        qty = int(row['qty'])
                        if row['item_type'] == "ChildrensBook":
                            children_book_count += qty
                            parent_status[p_id]['has_book'] = True
                        elif row['item_type'] == "AdultBook":
                            parent_status[p_id]['has_book'] = True
                        elif row['item_type'] == "BakedGood":
                            parent_status[p_id]['has_bake'] = True
            except: continue

    # 4. Filter VIPs
    vip_first_names = []
    for p_id, status in parent_status.items():
        if status['has_book'] and status['has_bake']:
            full_name = parent_map.get(p_id, "")
            first_name = full_name.split(' ')[0]
            if first_name:
                vip_first_names.append(first_name)
                
    return children_book_count, sorted(list(set(vip_first_names)))

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []
    
    target_file = os.path.join(workspace, "deliverables/gala_summary.json")
    
    # Check 1: File existence (10 points)
    if os.path.exists(target_file):
        score += 10
        details.append({"item": "File existence", "score": 10, "max_score": 10, "passed": True, "reason": "gala_summary.json exists."})
    else:
        details.append({"item": "File existence", "score": 0, "max_score": 10, "passed": False, "reason": "gala_summary.json not found."})
        # If file is missing, we still run the logic to see what it should have been for the log, but score ends here
        print(json.dumps({"total_score": 0, "details": details}))
        return

    # Check 2: JSON formatting (10 points)
    try:
        with open(target_file, 'r') as f:
            output_data = json.load(f)
        score += 10
        details.append({"item": "JSON formatting", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON format."})
    except Exception as e:
        details.append({"item": "JSON formatting", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        print(json.dumps({"total_score": score, "details": details}))
        return

    # Get Truth
    truth_count, truth_vips = calculate_ground_truth(workspace)
    
    # Check 3: ChildrensBook Count (40 points)
    agent_count = output_data.get("children_book_total", -1)
    if agent_count == truth_count:
        score += 40
        details.append({"item": "ChildrensBook total count", "score": 40, "max_score": 40, "passed": True, "reason": f"Correct count: {truth_count}"})
    else:
        details.append({"item": "ChildrensBook total count", "score": 0, "max_score": 40, "passed": False, "reason": f"Expected {truth_count}, got {agent_count}"})

    # Check 4: VIP First Names (40 points)
    agent_vips = output_data.get("vip_first_names", [])
    if isinstance(agent_vips, list):
        agent_vips_sorted = sorted([str(v) for v in agent_vips])
        truth_vips_sorted = sorted(truth_vips)
        
        if agent_vips_sorted == truth_vips_sorted:
            score += 40
            details.append({"item": "VIP first names list", "score": 40, "max_score": 40, "passed": True, "reason": "VIP list is perfectly matched."})
        else:
            # Partial credit for overlap? No, strict filtering is required here.
            # But let's check if there's any overlap to provide better feedback
            common = set(agent_vips_sorted) & set(truth_vips_sorted)
            reason = f"Mismatch. Expected {len(truth_vips_sorted)} names, got {len(agent_vips_sorted)}."
            if not common and len(truth_vips_sorted) > 0:
                reason += " Zero overlap found."
            details.append({"item": "VIP first names list", "score": 0, "max_score": 40, "passed": False, "reason": reason})
    else:
        details.append({"item": "VIP first names list", "score": 0, "max_score": 40, "passed": False, "reason": "vip_first_names is not a list."})

    # Final Output
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
