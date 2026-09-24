import os
import sys
import json
import re
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def compute_gold_standard(workspace):
    """
    Recalculate the exact expected values by simulating the ideal agent logic over the actual generated files.
    This guarantees 100% accuracy without hardcoding numbers, in case environment seeds change.
    """
    target_date = "2024-10-31"
    target_building = "Oakwood"
    
    valid_units = {}
    base_dir = os.path.join(workspace, "inspection_notes")
    
    if not os.path.exists(base_dir):
        return None, None
        
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
                
            if "[VOID]" in content:
                continue
                
            date_match = re.search(r"Date:\s*(.+)", content)
            building_match = re.search(r"Building:\s*(.+)", content)
            unit_match = re.search(r"Unit:\s*(\d+)", content)
            
            if not (date_match and building_match and unit_match):
                continue
                
            date = date_match.group(1).strip()
            building = building_match.group(1).strip()
            unit_id = int(unit_match.group(1).strip())
            
            if date != target_date or building != target_building:
                continue
                
            spray_match = re.search(r"\[SPRAY:\s*([0-9.]+)\s*oz\]", content)
            empty_match = re.search(r"\[EMPTY_STATIONS:\s*(\d+)\]", content)
            
            if not (spray_match and empty_match):
                continue
                
            spray = float(spray_match.group(1))
            empty = int(empty_match.group(1))
            is_revised = "_revised" in f
            
            if unit_id not in valid_units:
                valid_units[unit_id] = {"spray": spray, "empty": empty, "revised": is_revised}
            else:
                if is_revised:
                    valid_units[unit_id] = {"spray": spray, "empty": empty, "revised": True}
                    
    total_spray = round(sum(v["spray"] for v in valid_units.values()), 1)
    total_empty = sum(v["empty"] for v in valid_units.values())
    
    return total_spray, total_empty

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    # Pre-calculate gold standard
    gold_spray, gold_empty = compute_gold_standard(workspace)
    
    # 1. Check reports directory
    reports_dir = os.path.join(workspace, "reports")
    dir_exists = os.path.isdir(reports_dir)
    score_details.append({
        "item": "Directory 'reports' exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Found 'reports' directory" if dir_exists else "Missing 'reports' directory"
    })
    if dir_exists:
        total_score += 10
        
    # 2. Check totals.json file
    json_path = os.path.join(reports_dir, "totals.json")
    file_exists = os.path.isfile(json_path)
    score_details.append({
        "item": "File 'reports/totals.json' exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "Found 'totals.json'" if file_exists else "Missing 'totals.json'"
    })
    if file_exists:
        total_score += 10
        
    agent_spray, agent_empty = None, None
    valid_schema = False
    
    # 3. Check JSON schema and constraints
    if file_exists:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                keys = set(data.keys())
                expected_keys = {"total_spray_oz", "total_empty_stations"}
                if keys == expected_keys:
                    try:
                        agent_spray = float(data["total_spray_oz"])
                        agent_empty = int(data["total_empty_stations"])
                        valid_schema = True
                    except ValueError:
                        pass
        except Exception:
            pass

    score_details.append({
        "item": "Valid JSON format and exact keys present",
        "score": 20 if valid_schema else 0,
        "max_score": 20,
        "passed": valid_schema,
        "reason": "JSON schema matches exact requirements" if valid_schema else "JSON is invalid, missing keys, or contains extra keys"
    })
    if valid_schema:
        total_score += 20
        
    # 4 & 5. Check calculation accuracy
    if gold_spray is not None and gold_empty is not None:
        # Check spray logic (30 points)
        spray_correct = (valid_schema and abs(agent_spray - gold_spray) < 0.15)
        score_details.append({
            "item": "Total Spray Ounces is exactly correct",
            "score": 30 if spray_correct else 0,
            "max_score": 30,
            "passed": spray_correct,
            "reason": f"Expected ~{gold_spray}, got {agent_spray}" if not spray_correct else f"Matched expected spray {gold_spray}"
        })
        if spray_correct:
            total_score += 30
            
        # Check empty stations logic (30 points)
        empty_correct = (valid_schema and agent_empty == gold_empty)
        score_details.append({
            "item": "Total Empty Stations is exactly correct",
            "score": 30 if empty_correct else 0,
            "max_score": 30,
            "passed": empty_correct,
            "reason": f"Expected {gold_empty}, got {agent_empty}" if not empty_correct else f"Matched expected empty stations {gold_empty}"
        })
        if empty_correct:
            total_score += 30
    else:
        # Failsafe if workspace is deeply broken
        score_details.append({
            "item": "Math check skipped",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "Could not compute gold standard (missing files in workspace)"
        })

    # Write output report
    report_path = os.path.join(workspace, "workplace_score.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2)

if __name__ == "__main__":
    main()
