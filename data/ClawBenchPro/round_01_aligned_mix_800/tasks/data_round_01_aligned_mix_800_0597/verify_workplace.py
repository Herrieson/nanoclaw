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

def get_ground_truth(workspace):
    base_dir = os.path.join(workspace, "messy_stuff")
    targets = {}
    if not os.path.exists(base_dir):
        return targets
    for root, _, files in os.walk(base_dir):
        for f in files:
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    if isinstance(data, dict):
                        if data.get("author") == "WiscArt99" and data.get("tier") in ["Epic", "Legendary"]:
                            if "item_name" in data and "color" in data:
                                targets[data["item_name"]] = data["color"]
            except Exception:
                pass
    return targets

def extract_all_strings(data):
    """Recursively extract all string values and keys from JSON data."""
    strings = set()
    if isinstance(data, dict):
        for k, v in data.items():
            strings.add(str(k))
            strings.update(extract_all_strings(v))
    elif isinstance(data, list):
        for item in data:
            strings.update(extract_all_strings(item))
    elif isinstance(data, str):
        strings.add(data)
    return strings

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    target_dir = os.path.join(workspace, "fixed_assets")
    target_file = os.path.join(target_dir, "my_mod_pack.json")
    
    # 1. Check Directory
    if os.path.isdir(target_dir):
        results.append({"item": "Directory `fixed_assets` exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory exists."})
        total_score += 10
    else:
        results.append({"item": "Directory `fixed_assets` exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory not found."})

    # 2. Check File and JSON format
    agent_data = None
    if os.path.isfile(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                agent_data = json.load(f)
            results.append({"item": "File `my_mod_pack.json` exists and is valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON format."})
            total_score += 10
        except Exception as e:
            results.append({"item": "File `my_mod_pack.json` exists and is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"File missing or invalid JSON: {e}"})
    else:
        results.append({"item": "File `my_mod_pack.json` exists and is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "File not found."})

    # 3. Validation
    if agent_data is not None:
        truth = get_ground_truth(workspace)
        agent_strings = extract_all_strings(agent_data)
        
        # 3.1 Recall: Missing targets
        found_targets = 0
        for t_name in truth.keys():
            if any(t_name in s for s in agent_strings):
                found_targets += 1
                
        expected_count = max(len(truth), 1)
        recall_ratio = found_targets / expected_count
        recall_score = int(40 * recall_ratio)
        results.append({
            "item": "Recall of target items", 
            "score": recall_score, 
            "max_score": 40, 
            "passed": recall_score == 40, 
            "reason": f"Found {found_targets}/{len(truth)} targets."
        })
        total_score += recall_score

        # 3.2 Precision: Hallucinations and Decoys
        decoy_keywords = ["FakeItem", "Decoy", "Basic", "Missing Color", "SomeGuy", "WiscArt_99", "WISCART99"]
        found_decoys = []
        for s in agent_strings:
            for d in decoy_keywords:
                if d in s:
                    found_decoys.append(s)
        
        if len(found_decoys) == 0:
            results.append({"item": "Precision and robustness against decoys", "score": 40, "max_score": 40, "passed": True, "reason": "No decoys or garbage data found."})
            total_score += 40
        else:
            penalty = min(len(found_decoys) * 10, 40)
            precision_score = 40 - penalty
            results.append({"item": "Precision and robustness against decoys", "score": precision_score, "max_score": 40, "passed": False, "reason": f"Found {len(found_decoys)} decoy items/strings, penalizing {penalty} points."})
            total_score += precision_score
    else:
        results.append({"item": "Recall of target items", "score": 0, "max_score": 40, "passed": False, "reason": "No valid JSON data to evaluate."})
        results.append({"item": "Precision and robustness against decoys", "score": 0, "max_score": 40, "passed": False, "reason": "No valid JSON data to evaluate."})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2)

if __name__ == "__main__":
    main()
