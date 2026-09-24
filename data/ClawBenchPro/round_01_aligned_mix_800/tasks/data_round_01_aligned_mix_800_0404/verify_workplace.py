import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# Configuration for potential LLM usage (though this task is primarily structured)
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def calculate_ground_truth(workspace):
    """
    Replicate the logic from env_builder to get the exact expected values.
    """
    specs_path = os.path.join(workspace, 'lab_archive/equipment_manuals/calibration_specs.json')
    qc_path = os.path.join(workspace, 'lab_archive/qc_reports/daily/contamination_list.txt')
    runs_dir = os.path.join(workspace, 'lab_archive/runs')

    with open(specs_path, 'r') as f:
        specs = json.load(f)
    spectra_v_min = specs["current_machines"]["Spectra-V"]["min_rfu"]
    spectra_v_max = specs["current_machines"]["Spectra-V"]["max_rfu"]

    contaminated_samples = set()
    with open(qc_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("SMP-"):
                contaminated_samples.add(line)

    total_valid = 0
    sum_valid = 0.0

    for run_name in os.listdir(runs_dir):
        run_path = os.path.join(runs_dir, run_name)
        if not os.path.isdir(run_path):
            continue
        
        meta_path = os.path.join(run_path, 'metadata.json')
        csv_path = os.path.join(run_path, 'readings.csv')
        
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        
        if meta["machine"] == "Spectra-V" and meta["experiment_type"] == "in vivo metabolic":
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sid = row['sample_id']
                    rfu = float(row['rfu_value'])
                    if sid not in contaminated_samples:
                        if spectra_v_min <= rfu <= spectra_v_max:
                            total_valid += 1
                            sum_valid += rfu

    avg_valid = sum_valid / total_valid if total_valid > 0 else 0
    return total_valid, avg_valid

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    result_file = os.path.join(deliverables_dir, "clean_results.json")
    
    score = 0
    details = []

    # 1. Check directory and file existence (10 points)
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        score += 5
        details.append({"item": "Deliverables directory existence", "score": 5, "max_score": 5, "passed": True, "reason": "Directory exists."})
    else:
        details.append({"item": "Deliverables directory existence", "score": 0, "max_score": 5, "passed": False, "reason": "Directory not found."})

    if os.path.exists(result_file):
        score += 5
        details.append({"item": "Result file existence", "score": 5, "max_score": 5, "passed": True, "reason": "clean_results.json exists."})
    else:
        details.append({"item": "Result file existence", "score": 0, "max_score": 5, "passed": False, "reason": "clean_results.json not found."})
        # If no file, finalize and exit
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 2. Parse JSON and check structure (10 points)
    try:
        with open(result_file, 'r') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "JSON format and parsing", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON format."})
    except Exception as e:
        details.append({"item": "JSON format and parsing", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse JSON: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 3. Precise Data Validation (80 points)
    expected_count, expected_avg = calculate_ground_truth(workspace)
    
    # Extract keys (allow some flexibility in naming)
    agent_count = None
    agent_avg = None
    for k, v in data.items():
        if 'count' in k.lower() or 'total' in k.lower():
            agent_count = v
        if 'average' in k.lower() or 'mean' in k.lower() or 'rfu' in k.lower():
            agent_avg = v

    # Validate Count (40 points)
    if agent_count == expected_count:
        score += 40
        details.append({"item": "Accurate Sample Count", "score": 40, "max_score": 40, "passed": True, "reason": f"Count {agent_count} matches ground truth."})
    elif agent_count is not None and abs(agent_count - expected_count) < 5:
        score += 20
        details.append({"item": "Accurate Sample Count", "score": 20, "max_score": 40, "passed": False, "reason": f"Count {agent_count} is close but incorrect. Expected {expected_count}."})
    else:
        details.append({"item": "Accurate Sample Count", "score": 0, "max_score": 40, "passed": False, "reason": f"Count {agent_count} is incorrect or missing. Expected {expected_count}."})

    # Validate Average (40 points)
    if agent_avg is not None:
        try:
            if abs(float(agent_avg) - expected_avg) < 0.01:
                score += 40
                details.append({"item": "Accurate Average RFU", "score": 40, "max_score": 40, "passed": True, "reason": f"Average {agent_avg} matches ground truth."})
            elif abs(float(agent_avg) - expected_avg) < 1.0:
                score += 20
                details.append({"item": "Accurate Average RFU", "score": 20, "max_score": 40, "passed": False, "reason": f"Average {agent_avg} is close but lacks precision. Expected {expected_avg}."})
            else:
                details.append({"item": "Accurate Average RFU", "score": 0, "max_score": 40, "passed": False, "reason": f"Average {agent_avg} is significantly different from {expected_avg}."})
        except:
            details.append({"item": "Accurate Average RFU", "score": 0, "max_score": 40, "passed": False, "reason": "Average value is not a number."})
    else:
        details.append({"item": "Accurate Average RFU", "score": 0, "max_score": 40, "passed": False, "reason": "Average value missing."})

    # Final Score Output
    final_output = {
        "total_score": int(score),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(final_output, f, indent=2)

if __name__ == "__main__":
    verify()
