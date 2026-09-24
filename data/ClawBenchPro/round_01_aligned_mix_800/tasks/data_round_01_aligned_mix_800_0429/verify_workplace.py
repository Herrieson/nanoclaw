import os
import sys
import json
import csv
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize client, disable SSL verification
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

def calculate_ground_truth(workspace):
    # Calculate truth locally
    manifest_path = os.path.join(workspace, "scans", "qa_manifest_v2_final.log")
    if not os.path.exists(manifest_path):
        return None
    
    approved_batches = set()
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            if "Status: Approved" in line:
                try:
                    batch_name = line.split("Inspected ")[1].split(" by")[0].strip()
                    approved_batches.add(batch_name)
                except Exception:
                    pass

    seen_ids = set()
    broken_count = 0
    duplicate_count = 0
    valid_records = {}

    for batch in approved_batches:
        batch_dir = os.path.join(workspace, "scans", batch)
        if not os.path.exists(batch_dir): continue
        for root, dirs, files in os.walk(batch_dir):
            for file in files:
                if not file.endswith(".csv"): continue
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as csvf:
                    reader = csv.reader(csvf)
                    try:
                        headers = next(reader)
                    except StopIteration:
                        continue
                    
                    id_idx, title_idx = -1, -1
                    for i, h in enumerate(headers):
                        if h in ["Call_Number", "ID", "ref_no"]: id_idx = i
                        elif h in ["Title", "Book_Name", "name"]: title_idx = i
                    
                    for row in reader:
                        if id_idx == -1 or title_idx == -1 or len(row) <= max(id_idx, title_idx):
                            broken_count += 1
                            continue
                        
                        c_id = row[id_idx].strip()
                        title = row[title_idx].strip()
                        
                        if not c_id or not title:
                            broken_count += 1
                        else:
                            if c_id in seen_ids:
                                duplicate_count += 1
                            else:
                                seen_ids.add(c_id)
                                valid_records[c_id] = title

    return {
        "valid_records": valid_records,
        "unique_count": len(valid_records),
        "broken_count": broken_count,
        "duplicate_count": duplicate_count,
        "total_cost": len(valid_records) * 12.50
    }

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    report_dir = os.path.join(workspace, "archive_report")
    catalog_path = os.path.join(report_dir, "catalog.json")
    summary_path = os.path.join(report_dir, "summary.txt")

    # 1. Directory and Files Existence
    if os.path.isdir(report_dir) and os.path.isfile(catalog_path) and os.path.isfile(summary_path):
        score_details.append({"item": "Check existence of archive_report folder and required files", "score": 10, "max_score": 10, "passed": True, "reason": "All required files found."})
        total_score += 10
    else:
        score_details.append({"item": "Check existence of archive_report folder and required files", "score": 0, "max_score": 10, "passed": False, "reason": "Missing directory or report files."})

    # Get Ground Truth
    gt = calculate_ground_truth(workspace)

    # 2. catalog.json structural validity and keys
    catalog_data = None
    if os.path.isfile(catalog_path):
        try:
            with open(catalog_path, "r", encoding="utf-8") as f:
                catalog_data = json.load(f)
            if isinstance(catalog_data, list) and all(isinstance(r, dict) for r in catalog_data):
                keys_valid = True
                for row in catalog_data:
                    if set(row.keys()) != {"Call_Number", "Title"}:
                        keys_valid = False
                        break
                
                if keys_valid:
                    score_details.append({"item": "Check catalog.json schema and keys", "score": 20, "max_score": 20, "passed": True, "reason": "catalog.json is a list of objects with exactly 'Call_Number' and 'Title'."})
                    total_score += 20
                else:
                    score_details.append({"item": "Check catalog.json schema and keys", "score": 5, "max_score": 20, "passed": False, "reason": "catalog.json structure is partially correct but has wrong or extra keys."})
                    total_score += 5
            else:
                score_details.append({"item": "Check catalog.json schema and keys", "score": 0, "max_score": 20, "passed": False, "reason": "catalog.json is not a valid list of dicts."})
        except Exception as e:
            score_details.append({"item": "Check catalog.json schema and keys", "score": 0, "max_score": 20, "passed": False, "reason": f"Failed to parse catalog.json: {e}"})
    else:
        score_details.append({"item": "Check catalog.json schema and keys", "score": 0, "max_score": 20, "passed": False, "reason": "catalog.json missing."})

    # 3. Data Integrity & Correctness Check (Ground truth comparison)
    if gt is not None and catalog_data and isinstance(catalog_data, list):
        agent_records = {r.get("Call_Number"): r.get("Title") for r in catalog_data if "Call_Number" in r}
        
        if len(agent_records) == gt["unique_count"] and set(agent_records.keys()) == set(gt["valid_records"].keys()):
            score_details.append({"item": "Validate precision of unique records in catalog.json", "score": 30, "max_score": 30, "passed": True, "reason": "Extracted exactly the matching set of uniquely valid records."})
            total_score += 30
        else:
            diff_len = abs(len(agent_records) - gt["unique_count"])
            if diff_len < 10: # Partial credit for being very close
                score_details.append({"item": "Validate precision of unique records in catalog.json", "score": 10, "max_score": 30, "passed": False, "reason": f"Data mismatch, slightly off by {diff_len} records. Likely logic flaws."})
                total_score += 10
            else:
                score_details.append({"item": "Validate precision of unique records in catalog.json", "score": 0, "max_score": 30, "passed": False, "reason": "Substantial data mismatch."})
    else:
         score_details.append({"item": "Validate precision of unique records in catalog.json", "score": 0, "max_score": 30, "passed": False, "reason": "Cannot compare due to previous failures or missing ground truth."})

    # 4. LLM semantic check on summary.txt
    if os.path.isfile(summary_path) and gt is not None:
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                summary_content = f.read()
            
            prompt = (
                "You are evaluating an archive summary text. Check if the text explicitly states ALL the following accurate numbers:\n"
                f"- Unique valid records: {gt['unique_count']}\n"
                f"- Broken records: {gt['broken_count']}\n"
                f"- Duplicate records: {gt['duplicate_count']}\n"
                f"- Total cost: {gt['total_cost']} (or {gt['total_cost']:.2f})\n\n"
                "If it contains these exact numbers and associates them correctly with their meaning, answer YES. Otherwise, answer NO."
            )
            
            if llm_judge_content(prompt, summary_content):
                score_details.append({"item": "LLM check summary.txt for accurate counts and cost", "score": 40, "max_score": 40, "passed": True, "reason": "Summary text accurately reflects all analytical numbers."})
                total_score += 40
            else:
                score_details.append({"item": "LLM check summary.txt for accurate counts and cost", "score": 0, "max_score": 40, "passed": False, "reason": "LLM judged summary.txt is missing correct numbers or mapping is wrong."})
        except Exception as e:
            score_details.append({"item": "LLM check summary.txt for accurate counts and cost", "score": 0, "max_score": 40, "passed": False, "reason": f"Error reading summary or LLM failure: {e}"})
    else:
        score_details.append({"item": "LLM check summary.txt for accurate counts and cost", "score": 0, "max_score": 40, "passed": False, "reason": "summary.txt missing or ground truth missing."})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
