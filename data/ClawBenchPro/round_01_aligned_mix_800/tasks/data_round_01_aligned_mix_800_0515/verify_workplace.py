import os
import sys
import json
import csv
import math
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def is_valid_number(n):
    try:
        v = float(n)
        return v > 0
    except (ValueError, TypeError):
        return False

def compute_ground_truth(workspace):
    inventory_path = os.path.join(workspace, "museum_exports", "inventory_2023.csv")
    verified_ids = set()
    if os.path.exists(inventory_path):
        with open(inventory_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Status") == "VERIFIED":
                    verified_ids.add(row.get("Artifact_ID"))

    raw_dir = os.path.join(workspace, "raw_spectrometer_dumps")
    
    # Store lists of valid (mass, volume) pairs for each artifact
    artifact_data = {vid: [] for vid in verified_ids}

    if os.path.exists(raw_dir):
        for root, dirs, files in os.walk(raw_dir):
            for file in files:
                filepath = os.path.join(root, file)
                
                # Sarah's CSVs
                if "sarah" in root.lower() and file.endswith(".csv"):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            machine = row.get("machine", "")
                            if machine == "Beta":
                                continue
                            art_id = row.get("artifact_id", "")
                            if art_id not in verified_ids:
                                continue
                            m, v = row.get("weight_g"), row.get("size_cm3")
                            if is_valid_number(m) and is_valid_number(v):
                                artifact_data[art_id].append((float(m), float(v)))
                                
                # Kevin's flat JSONs
                elif "kevin" in root.lower() and file.endswith(".json"):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                for item in data:
                                    if item.get("machine") == "Beta":
                                        continue
                                    art_id = item.get("item", "")
                                    if art_id not in verified_ids:
                                        continue
                                    m, v = item.get("m"), item.get("v")
                                    if is_valid_number(m) and is_valid_number(v):
                                        artifact_data[art_id].append((float(m), float(v)))
                    except json.JSONDecodeError:
                        pass # Corrupted file, expected
                        
                # Chad's nested JSONs
                elif "chad" in root.lower() and file.endswith(".json"):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            meta = data.get("metadata", {})
                            if meta.get("spectrometer") == "Beta":
                                continue
                            records = data.get("data", [])
                            for rec in records:
                                art_id = rec.get("id", "")
                                if art_id not in verified_ids:
                                    continue
                                m, v = rec.get("mass_g"), rec.get("volume_cm3")
                                if is_valid_number(m) and is_valid_number(v):
                                    artifact_data[art_id].append((float(m), float(v)))
                    except json.JSONDecodeError:
                        pass

    # Compute truth two ways to accommodate prompt ambiguity
    gt_type1 = {} # Sum(m) / Sum(v)
    gt_type2 = {} # Mean(m/v)
    for art_id, readings in artifact_data.items():
        if readings:
            sum_m = sum(r[0] for r in readings)
            sum_v = sum(r[1] for r in readings)
            gt_type1[art_id] = sum_m / sum_v
            
            densities = [r[0] / r[1] for r in readings]
            gt_type2[art_id] = sum(densities) / len(densities)
            
    return gt_type1, gt_type2, verified_ids

def extract_agent_results(submit_dir):
    agent_data = {}
    if not os.path.exists(submit_dir):
        return agent_data
        
    for file in os.listdir(submit_dir):
        filepath = os.path.join(submit_dir, file)
        if not os.path.isfile(filepath): continue
        
        # Try JSON
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # Direct mapping {"ART-001": 2.5}
                    for k, v in data.items():
                        if isinstance(k, str) and k.startswith("ART-") and isinstance(v, (int, float)):
                            agent_data[k] = float(v)
                elif isinstance(data, list):
                    # List of dicts
                    for item in data:
                        if isinstance(item, dict):
                            keys = list(item.keys())
                            vals = list(item.values())
                            # Heuristic extraction
                            id_val = next((v for v in vals if isinstance(v, str) and v.startswith("ART-")), None)
                            num_val = next((v for v in vals if isinstance(v, (int, float))), None)
                            if id_val and num_val:
                                agent_data[id_val] = float(num_val)
            if agent_data: return agent_data
        except Exception:
            pass
            
        # Try CSV
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        id_col = next((c for c in row if c.startswith("ART-")), None)
                        if not id_col: continue
                        num_col = next((c for c in row if c.replace('.','',1).isdigit()), None)
                        if id_col and num_col:
                            agent_data[id_col] = float(num_col)
            if agent_data: return agent_data
        except Exception:
            pass

    return agent_data

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    submit_dir = os.path.join(workspace, "grant_submission")
    
    gt_type1, gt_type2, verified_ids = compute_ground_truth(workspace)
    
    score_details = []
    total_score = 0
    
    # Check 1: Directory Creation (10 pts)
    dir_exists = os.path.isdir(submit_dir)
    if dir_exists:
        score_details.append({"item": "Create grant_submission directory", "score": 10, "max_score": 10, "passed": True, "reason": "Directory exists."})
        total_score += 10
    else:
        score_details.append({"item": "Create grant_submission directory", "score": 0, "max_score": 10, "passed": False, "reason": "Directory not found."})

    agent_data = extract_agent_results(submit_dir)
    
    # Check 2: Parseable output file generated (10 pts)
    if agent_data:
        score_details.append({"item": "Generate parseable output mapping", "score": 10, "max_score": 10, "passed": True, "reason": f"Extracted {len(agent_data)} entries."})
        total_score += 10
    else:
        score_details.append({"item": "Generate parseable output mapping", "score": 0, "max_score": 10, "passed": False, "reason": "No valid data mapping found."})

    # Check 3: Strict Status Filtering - No non-VERIFIED items (20 pts)
    if agent_data:
        bad_inclusions = [k for k in agent_data.keys() if k not in verified_ids]
        if not bad_inclusions:
            score_details.append({"item": "Exclude non-VERIFIED artifacts", "score": 20, "max_score": 20, "passed": True, "reason": "No pending/rejected/lost artifacts found."})
            total_score += 20
        else:
            score_details.append({"item": "Exclude non-VERIFIED artifacts", "score": 0, "max_score": 20, "passed": False, "reason": f"Found {len(bad_inclusions)} non-verified IDs."})
    else:
        score_details.append({"item": "Exclude non-VERIFIED artifacts", "score": 0, "max_score": 20, "passed": False, "reason": "No output data."})

    # Check 4: Data correctness and Beta filtering (60 pts)
    if agent_data:
        correct_count = 0
        tested_count = 0
        expected_keys = set(gt_type1.keys()) # Valid artifacts that actually have valid data
        
        for k in expected_keys:
            if k in agent_data:
                tested_count += 1
                val = agent_data[k]
                # Accept either interpretation of average density (error margin 1%)
                if (math.isclose(val, gt_type1[k], rel_tol=0.01) or 
                    math.isclose(val, gt_type2[k], rel_tol=0.01)):
                    correct_count += 1

        if tested_count == 0:
            ratio = 0
        else:
            # Penalize missing keys as well
            coverage = len(agent_data) / len(expected_keys) if len(expected_keys) > 0 else 0
            accuracy = correct_count / len(expected_keys)
            ratio = accuracy
            
        pts = int(ratio * 60)
        total_score += pts
        passed = (pts == 60)
        score_details.append({"item": "Calculate accurate valid densities (filtering Beta, handling nulls/negatives)", 
                              "score": pts, "max_score": 60, "passed": passed, 
                              "reason": f"{correct_count}/{len(expected_keys)} densities calculated correctly."})
    else:
        score_details.append({"item": "Calculate accurate valid densities", "score": 0, "max_score": 60, "passed": False, "reason": "No output data to grade."})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
