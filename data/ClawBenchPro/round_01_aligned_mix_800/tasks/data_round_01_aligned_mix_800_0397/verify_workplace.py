import os
import sys
import json
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

def extract_all_strings(data):
    """Recursively extract all strings from a JSON object (keys and values)."""
    strings = set()
    if isinstance(data, dict):
        for k, v in data.items():
            strings.add(str(k).strip())
            strings.update(extract_all_strings(v))
    elif isinstance(data, list):
        for item in data:
            strings.update(extract_all_strings(item))
    elif data is not None:
        strings.add(str(data).strip())
    return strings

def check_workplace(workspace):
    score_details = []
    total_score = 0
    
    output_dir = os.path.join(workspace, "fixed_assets")
    output_file = os.path.join(output_dir, "my_mod_pack.json")
    
    # 1. Check directory existence
    if os.path.isdir(output_dir):
        total_score += 10
        score_details.append({"item": "Create fixed_assets directory", "score": 10, "max_score": 10, "passed": True, "reason": "Directory exists."})
    else:
        score_details.append({"item": "Create fixed_assets directory", "score": 0, "max_score": 10, "passed": False, "reason": "Directory missing."})
        
    # 2. Check file existence
    if os.path.isfile(output_file):
        total_score += 10
        score_details.append({"item": "Create my_mod_pack.json file", "score": 10, "max_score": 10, "passed": True, "reason": "File exists."})
    else:
        score_details.append({"item": "Create my_mod_pack.json file", "score": 0, "max_score": 10, "passed": False, "reason": "File missing."})
        
    # JSON Parsing and Content Verification
    if os.path.isfile(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            total_score += 10
            score_details.append({"item": "Valid JSON format", "score": 10, "max_score": 10, "passed": True, "reason": "File successfully parsed as JSON."})
            
            all_strings = extract_all_strings(json_data)
            
            # Target 1 Verification
            t1_pass = "Frostbite Sword" in all_strings and "#00FFFF" in all_strings
            if t1_pass:
                total_score += 15
            score_details.append({"item": "Extract Target 1 (Frostbite Sword)", "score": 15 if t1_pass else 0, "max_score": 15, "passed": t1_pass, "reason": "Found Frostbite Sword and its color." if t1_pass else "Missing Frostbite Sword or its color."})
            
            # Target 2 Verification
            t2_pass = "Cheese Crown" in all_strings and "#FFD700" in all_strings
            if t2_pass:
                total_score += 15
            score_details.append({"item": "Extract Target 2 (Cheese Crown)", "score": 15 if t2_pass else 0, "max_score": 15, "passed": t2_pass, "reason": "Found Cheese Crown and its color." if t2_pass else "Missing Cheese Crown or its color."})
            
            # Target 3 Verification
            t3_pass = "Cranberry Potion" in all_strings and "#AA0033" in all_strings
            if t3_pass:
                total_score += 15
            score_details.append({"item": "Extract Target 3 (Cranberry Potion)", "score": 15 if t3_pass else 0, "max_score": 15, "passed": t3_pass, "reason": "Found Cranberry Potion and its color." if t3_pass else "Missing Cranberry Potion or its color."})
            
            # Junk Exclusion Verification
            j1_pass = "Lame Axe" not in all_strings and "#FF0000" not in all_strings
            if j1_pass:
                total_score += 15
            score_details.append({"item": "Exclude Junk 1 (Wrong Author)", "score": 15 if j1_pass else 0, "max_score": 15, "passed": j1_pass, "reason": "Correctly ignored SomeGuy_88's Lame Axe." if j1_pass else "Incorrectly included Lame Axe."})
            
            j2_pass = "Basic Boots" not in all_strings and "#888888" not in all_strings
            if j2_pass:
                total_score += 10
            score_details.append({"item": "Exclude Junk 2 (Wrong Tier)", "score": 10 if j2_pass else 0, "max_score": 10, "passed": j2_pass, "reason": "Correctly ignored Common tier Basic Boots." if j2_pass else "Incorrectly included Basic Boots."})
            
        except json.JSONDecodeError:
            score_details.append({"item": "Valid JSON format", "score": 0, "max_score": 10, "passed": False, "reason": "File is not a valid JSON structure."})
            score_details.append({"item": "Content verification", "score": 0, "max_score": 70, "passed": False, "reason": "Failed to parse JSON, skipping content verification."})
    else:
        score_details.append({"item": "Content verification", "score": 0, "max_score": 80, "passed": False, "reason": "Missing output file, cannot verify content."})

    # Write results
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    check_workplace(workspace)
