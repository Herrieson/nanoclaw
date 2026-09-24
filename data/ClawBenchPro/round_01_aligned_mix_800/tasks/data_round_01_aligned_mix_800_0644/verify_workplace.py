import os
import sys
import json
import httpx
from openai import OpenAI
import glob
import math

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

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

def find_rep_stats(node, rep_name):
    """Recursively search for a dictionary that seems to describe the stats for a given sales rep."""
    if isinstance(node, dict):
        # If the rep_name is a value in the dict (e.g., {"name": "Carlos", ...})
        if any(isinstance(v, str) and rep_name.lower() in v.lower() for v in node.values()):
            return node
        # Or if the rep_name is a key (e.g., {"Carlos": {...}})
        for k, v in node.items():
            if rep_name.lower() in k.lower() and isinstance(v, dict):
                return v
        # Otherwise keep searching
        for v in node.values():
            result = find_rep_stats(v, rep_name)
            if result:
                return result
    elif isinstance(node, list):
        for item in node:
            result = find_rep_stats(item, rep_name)
            if result:
                return result
    return None

def find_missing_forms(node):
    """Recursively gather all strings in lists or dicts that might be contract IDs."""
    found_contracts = set()
    if isinstance(node, dict):
        for k, v in node.items():
            # If key implies missing or flagged, extract values
            if any(kw in k.lower() for kw in ["miss", "flag", "uncompli", "without", "lack"]):
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, str):
                            found_contracts.add(item.strip())
                elif isinstance(v, str):
                    found_contracts.add(v.strip())
            else:
                found_contracts.update(find_missing_forms(v))
    elif isinstance(node, list):
        for item in node:
            found_contracts.update(find_missing_forms(item))
    return found_contracts

def is_ratio_close(val, expected=2/3):
    try:
        f_val = float(val)
        # Check against 0.66, 0.67, 66.6%, etc.
        if 0.66 <= f_val <= 0.67 or 66 <= f_val <= 67:
            return True
    except:
        pass
    if isinstance(val, str):
        if "2/3" in val or "66.6" in val or "66.7" in val:
            return True
    return False

def is_count_correct(val, expected=2):
    try:
        return int(val) == expected
    except:
        pass
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score = 0
    details = []

    # 1. Directory and JSON File Existence
    if os.path.isdir(deliverables_dir):
        json_files = glob.glob(os.path.join(deliverables_dir, "*.json"))
        if json_files:
            score += 20
            details.append({"item": "JSON file existence in deliverables", "score": 20, "max_score": 20, "passed": True, "reason": "Found JSON file(s)."})
            target_json = json_files[0]
        else:
            details.append({"item": "JSON file existence in deliverables", "score": 0, "max_score": 20, "passed": False, "reason": "No JSON file found in deliverables directory."})
            target_json = None
    else:
        details.append({"item": "JSON file existence in deliverables", "score": 0, "max_score": 20, "passed": False, "reason": "deliverables directory not found."})
        target_json = None

    if not target_json:
        # Cannot proceed without JSON
        for step in ["JSON parsing", "Carlos Stats", "Sarah Stats", "Flagged Missing Contracts"]:
            details.append({"item": step, "score": 0, "max_score": 20, "passed": False, "reason": "Skipped due to missing JSON file."})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # 2. JSON Parsing
    parsed_data = None
    try:
        with open(target_json, "r") as f:
            parsed_data = json.load(f)
        score += 10
        details.append({"item": "JSON parsing", "score": 10, "max_score": 10, "passed": True, "reason": "Successfully parsed JSON structure."})
    except Exception as e:
        details.append({"item": "JSON parsing", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse JSON: {e}"})

    if not parsed_data:
        # Cannot proceed
        for step in ["Carlos Stats", "Sarah Stats", "Flagged Missing Contracts"]:
            details.append({"item": step, "score": 0, "max_score": 23, "passed": False, "reason": "Skipped due to invalid JSON data."})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # 3. Carlos Stats (20)
    carlos_node = find_rep_stats(parsed_data, "Carlos")
    if carlos_node:
        vals = list(carlos_node.values())
        has_count = any(is_count_correct(v, 2) for v in vals)
        has_ratio = any(is_ratio_close(v) for v in vals)
        
        c_score = 0
        if has_count: c_score += 10
        if has_ratio: c_score += 10
        
        score += c_score
        details.append({"item": "Carlos Stats", "score": c_score, "max_score": 20, "passed": c_score == 20, "reason": f"Count correct: {has_count}, Ratio correct: {has_ratio}"})
    else:
        details.append({"item": "Carlos Stats", "score": 0, "max_score": 20, "passed": False, "reason": "Could not locate Carlos stats in JSON."})

    # 4. Sarah Stats (20)
    sarah_node = find_rep_stats(parsed_data, "Sarah")
    if sarah_node:
        vals = list(sarah_node.values())
        has_count = any(is_count_correct(v, 2) for v in vals)
        has_ratio = any(is_ratio_close(v) for v in vals)
        
        s_score = 0
        if has_count: s_score += 10
        if has_ratio: s_score += 10
        
        score += s_score
        details.append({"item": "Sarah Stats", "score": s_score, "max_score": 20, "passed": s_score == 20, "reason": f"Count correct: {has_count}, Ratio correct: {has_ratio}"})
    else:
        details.append({"item": "Sarah Stats", "score": 0, "max_score": 20, "passed": False, "reason": "Could not locate Sarah stats in JSON."})

    # 5. Flagged Missing Contracts (30)
    missing_contracts = find_missing_forms(parsed_data)
    # Also check a broader condition just in case the key wasn't caught by keywords
    json_str = json.dumps(parsed_data)
    has_003 = "CTX-003" in json_str
    
    if "CTX-003" in missing_contracts and len(missing_contracts) == 1:
        score += 30
        details.append({"item": "Flagged Missing Contracts", "score": 30, "max_score": 30, "passed": True, "reason": "Correctly flagged only CTX-003 as missing."})
    elif "CTX-003" in missing_contracts:
        score += 15
        details.append({"item": "Flagged Missing Contracts", "score": 15, "max_score": 30, "passed": False, "reason": "Flagged CTX-003 but also included extra/false contracts."})
    elif has_003:
        # Maybe our heuristic failed to map it exactly, use LLM as a fallback to confirm the context of "CTX-003"
        prompt = "Does the JSON clearly indicate that 'CTX-003' is missing a compliance form, missing a signed document, or uncompliant? It should ONLY be CTX-003."
        if llm_judge_content(prompt, json.dumps(parsed_data, indent=2)):
            score += 30
            details.append({"item": "Flagged Missing Contracts", "score": 30, "max_score": 30, "passed": True, "reason": "LLM verified that CTX-003 is flagged as missing compliance."})
        else:
            details.append({"item": "Flagged Missing Contracts", "score": 0, "max_score": 30, "passed": False, "reason": "CTX-003 is present in JSON but LLM could not verify it as the solitary missing compliance form."})
    else:
        details.append({"item": "Flagged Missing Contracts", "score": 0, "max_score": 30, "passed": False, "reason": "CTX-003 not identified as missing."})

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
