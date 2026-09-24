import os
import sys
import json
import re

def get_discharged_ids(workspace):
    log_path = os.path.join(workspace, "system_updates/daily_discharge.log")
    if not os.path.exists(log_path):
        return set()
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()
    return set(re.findall(r"PT-\d{4}", content))

def calculate_ground_truth(workspace):
    discharged_ids = get_discharged_ids(workspace)
    patient_dir = os.path.join(workspace, "patient_intake")
    nutrition_dir = os.path.join(workspace, "nutrition_orders")
    
    spanish_names = []
    dietary_names = []
    
    for root, dirs, files in os.walk(patient_dir):
        for file in files:
            if not file.endswith(".json") or file.endswith(".bak"):
                continue
            
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                
            p_id = data.get("patient_id")
            # Filter 1: Basic Status
            if data.get("admission_status") != "Active":
                continue
            # Filter 2: Log Override
            if p_id in discharged_ids:
                continue
            
            # Spanish Materials Check
            lang = data.get("demographics", {}).get("primary_language", "").lower()
            if any(key in lang for key in ["spanish", "es", "español"]):
                spanish_names.append(data.get("full_name"))
                
            # Dietary Restriction Check
            nut_id = data.get("nutrition_order_id")
            nut_file = os.path.join(nutrition_dir, f"{nut_id}.txt")
            if os.path.exists(nut_file):
                with open(nut_file, "r", encoding="utf-8") as f:
                    nut_content = f.read()
                # Extract instruction line
                instr_line = ""
                for line in nut_content.splitlines():
                    if "DIETARY INSTRUCTIONS:" in line:
                        instr_line = line.split(":", 1)[1].strip().lower()
                        break
                
                # Check if it's restrictive
                if instr_line and not any(kw in instr_line for kw in ["none", "regular", "n/a"]):
                    dietary_names.append(data.get("full_name"))
                    
    return set(spanish_names), set(dietary_names)

def run_verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = os.path.join(workspace, "nursing_station/shift_prep.json")
    score_file = "workplace_score.json"
    
    score = 0
    details = []
    
    # 1. Check file existence (10 points)
    if os.path.exists(output_file):
        score += 10
        details.append({"item": "File existence", "score": 10, "max_score": 10, "passed": True, "reason": "shift_prep.json exists"})
    else:
        details.append({"item": "File existence", "score": 0, "max_score": 10, "passed": False, "reason": "shift_prep.json not found"})
        # Write 0 and exit if file missing
        with open(score_file, "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 2. Check JSON Format (10 points)
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            agent_data = json.load(f)
        score += 10
        details.append({"item": "JSON Validity", "score": 10, "max_score": 10, "passed": True, "reason": "File is valid JSON"})
    except Exception as e:
        details.append({"item": "JSON Validity", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
        with open(score_file, "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 3. Content Accuracy
    gt_spanish, gt_dietary = calculate_ground_truth(workspace)
    
    agent_spanish = set(agent_data.get("spanish_materials", []))
    agent_dietary = set(agent_data.get("dietary_restrictions", []))
    
    # Spanish Materials Scoring (40 points)
    # Check for extra/missing
    if agent_spanish == gt_spanish:
        score += 40
        details.append({"item": "Spanish Materials Accuracy", "score": 40, "max_score": 40, "passed": True, "reason": "Perfect match"})
    else:
        # Partial credit: calculation based on intersection/union (Jaccard-like)
        intersection = agent_spanish.intersection(gt_spanish)
        union = agent_spanish.union(gt_spanish)
        ratio = len(intersection) / len(union) if union else 1.0
        partial = int(ratio * 40)
        score += partial
        details.append({"item": "Spanish Materials Accuracy", "score": partial, "max_score": 40, "passed": partial > 30, "reason": f"Partial match: {len(intersection)}/{len(gt_spanish)} correct"})

    # Dietary Restrictions Scoring (40 points)
    if agent_dietary == gt_dietary:
        score += 40
        details.append({"item": "Dietary Restrictions Accuracy", "score": 40, "max_score": 40, "passed": True, "reason": "Perfect match"})
    else:
        intersection = agent_dietary.intersection(gt_dietary)
        union = agent_dietary.union(gt_dietary)
        ratio = len(intersection) / len(union) if union else 1.0
        partial = int(ratio * 40)
        score += partial
        details.append({"item": "Dietary Restrictions Accuracy", "score": partial, "max_score": 40, "passed": partial > 30, "reason": f"Partial match: {len(intersection)}/{len(gt_dietary)} correct"})

    # Check for hallucination (hard penalty if Agent made up names not in environment)
    # Get all names in environment for validation
    all_names_in_env = set()
    for root, _, files in os.walk(os.path.join(workspace, "patient_intake")):
        for file in files:
            if file.endswith(".json") and not file.endswith(".bak"):
                with open(os.path.join(root, file), "r") as f:
                    all_names_in_env.add(json.load(f).get("full_name"))
    
    agent_all_names = agent_spanish.union(agent_dietary)
    hallucinated = agent_all_names - all_names_in_env
    if hallucinated:
        penalty = min(20, len(hallucinated) * 5)
        score = max(0, score - penalty)
        details.append({"item": "Hallucination Check", "score": -penalty, "max_score": 0, "passed": False, "reason": f"Found {len(hallucinated)} names not present in database"})

    with open(score_file, "w") as f:
        json.dump({"total_score": score, "details": details}, f)

if __name__ == "__main__":
    run_verify()
