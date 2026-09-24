import os
import sys
import json
import glob
import re

def calculate_ground_truth(workspace):
    """
    Replicate the logic from the environment builder to find the correct answer.
    This ensures the verification is robust against the random environment generation.
    """
    registry_path = os.path.join(workspace, "field_logs", "registry_fragments", "*.json")
    prod_active_nodes = set()
    
    # 1. Get Registry
    for reg_file in glob.glob(registry_path):
        with open(reg_file, 'r') as f:
            data = json.load(f)
            for node in data:
                if node.get("env") == "PROD" and node.get("status") == "active":
                    prod_active_nodes.add(node["id"])

    # 2. Parse Telemetry
    shards_dir = os.path.join(workspace, "field_logs", "telemetry_shards")
    compliant_ids = []
    total_power = 0.0
    
    # We walk through cycles 0-4 as created by env_builder
    for root, dirs, files in os.walk(shards_dir):
        # Exclude garbage folders
        if any(x in root for x in ["legacy", "test_bench", "overflow", "temp_cache"]):
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            node_id = None
            sag, freq, power = None, None, None
            
            if file.endswith(".json"):
                try:
                    with open(file_path, 'r') as f:
                        d = json.load(f)
                        node_id = d.get("n_id")
                        metrics = d.get("metrics", {})
                        sag = metrics.get("v_sag")
                        freq = metrics.get("f_dev")
                        power = metrics.get("p_mw")
                except: continue
            elif file.endswith(".txt"):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        # Format: HDR|ID|TELEMETRY\nVAL|SAG:val|FREQ:val|PWR:val
                        id_match = re.search(r"HDR\|(NODE_[A-F0-9]+)\|", content)
                        val_match = re.search(r"SAG:([\d.]+)\|FREQ:([\d.]+)\|PWR:([\d.]+)", content)
                        if id_match and val_match:
                            node_id = id_match.group(1)
                            sag = float(val_match.group(1))
                            freq = float(val_match.group(2))
                            power = float(val_match.group(3))
                except: continue
            
            if node_id in prod_active_nodes:
                # IEEE 1547 Compliance logic: sag < 0.05 AND freq <= 0.1
                if sag is not None and freq is not None:
                    if sag < 0.05 and freq <= 0.1:
                        compliant_ids.append(node_id)
                        total_power += (power if power else 0)

    return sorted(compliant_ids), round(total_power, 4)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = os.path.join(workspace, "grid_summary", "compliance_report.json")
    score_file = "workplace_score.json"
    
    score = 0
    details = []

    # 1. Check file existence
    if os.path.exists(output_file):
        score += 10
        details.append({"item": "Result file exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found compliance_report.json"})
        
        try:
            with open(output_file, 'r') as f:
                submission = json.load(f)
            
            # 2. Check structure
            if "compliant_node_ids" in submission and "total_dispatchable_mw" in submission:
                score += 10
                details.append({"item": "JSON schema check", "score": 10, "max_score": 10, "passed": True, "reason": "Required fields present"})
                
                # Calculate Truth
                true_ids, true_power = calculate_ground_truth(workspace)
                
                # 3. Check node IDs (Set match)
                sub_ids = sorted(submission.get("compliant_node_ids", []))
                if sub_ids == true_ids:
                    score += 40
                    details.append({"item": "Node ID accuracy", "score": 40, "max_score": 40, "passed": True, "reason": "All compliant PROD nodes correctly identified"})
                else:
                    # Partial credit for overlap
                    overlap = set(sub_ids).intersection(set(true_ids))
                    p_score = int(40 * (len(overlap) / max(len(true_ids), len(sub_ids), 1)))
                    score += p_score
                    details.append({"item": "Node ID accuracy (Partial)", "score": p_score, "max_score": 40, "passed": False, "reason": f"Mismatched IDs. Overlap: {len(overlap)}/{len(true_ids)}"})

                # 4. Check Power calculation (Float tolerance)
                sub_power = submission.get("total_dispatchable_mw", 0)
                if abs(sub_power - true_power) < 0.01:
                    score += 40
                    details.append({"item": "Power calculation accuracy", "score": 40, "max_score": 40, "passed": True, "reason": f"Calculated power {sub_power} matches ground truth"})
                elif abs(sub_power - true_power) < 1.0:
                    score += 20
                    details.append({"item": "Power calculation accuracy (Minor error)", "score": 20, "max_score": 40, "passed": False, "reason": "Calculation close but slightly off tolerance"})
                else:
                    details.append({"item": "Power calculation accuracy", "score": 0, "max_score": 40, "passed": False, "reason": f"Calculated power {sub_power} differs significantly from {true_power}"})

            else:
                details.append({"item": "JSON schema check", "score": 0, "max_score": 10, "passed": False, "reason": "Missing keys in JSON"})

        except Exception as e:
            details.append({"item": "JSON parse error", "score": 0, "max_score": 80, "passed": False, "reason": str(e)})
    else:
        details.append({"item": "Result file exists", "score": 0, "max_score": 100, "passed": False, "reason": "compliance_report.json not found"})

    with open(score_file, "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
