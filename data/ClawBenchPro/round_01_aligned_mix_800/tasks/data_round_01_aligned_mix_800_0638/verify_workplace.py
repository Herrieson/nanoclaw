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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    pantry_dir = os.path.join(workspace, "pantry_audit")
    summary_file = os.path.join(pantry_dir, "summary.json")

    # 1. Check directory existence
    if os.path.isdir(pantry_dir):
        score_details.append({"item": "pantry_audit directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory created successfully."})
        total_score += 10
    else:
        score_details.append({"item": "pantry_audit directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory not found."})

    # 2. Check summary.json existence & validity
    json_data = None
    if os.path.isfile(summary_file):
        try:
            with open(summary_file, "r") as f:
                json_data = json.load(f)
            score_details.append({"item": "summary.json is valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "File exists and is valid JSON."})
            total_score += 10
        except json.JSONDecodeError:
            score_details.append({"item": "summary.json is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "File exists but is not valid JSON."})
    else:
        score_details.append({"item": "summary.json is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "File summary.json not found."})

    # Stop here if no valid json
    if not json_data:
        for _ in range(4):
            score_details.append({"item": "Subsequent JSON checks", "score": 0, "max_score": 20, "passed": False, "reason": "Skipped due to missing or invalid JSON."})
        
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Helper function to find nested keys loosely
    def find_val(data, target_keys, expected_type=None):
        if isinstance(data, dict):
            for k, v in data.items():
                if any(tk.lower() in k.lower() for tk in target_keys):
                    return v
                res = find_val(v, target_keys, expected_type)
                if res is not None:
                    return res
        return None

    # 3. Check Exact Spendings for Produce and Grains
    # Produce = Apples (15) + Potatoes (6) + Carrots (4) = 25
    # Grains = Flour (4) + Sugar (5) + Yeast (7.5) = 16.5
    json_str = json.dumps(json_data, indent=2).lower()
    
    produce_correct = "25" in json_str or "25.0" in json_str
    grains_correct = "16.5" in json_str or "16.50" in json_str

    if produce_correct and grains_correct:
        score_details.append({"item": "Produce and Grains spending accurate", "score": 25, "max_score": 25, "passed": True, "reason": "Accurately calculated Produce (25) and Grains (16.5)."})
        total_score += 25
    else:
        score_details.append({"item": "Produce and Grains spending accurate", "score": 0, "max_score": 25, "passed": False, "reason": "Failed to strictly calculate exact cost for Produce (25.0) and Grains (16.50)."})

    # 4. Check Protein spending (accepting either 47.0 if deduplicated or 59.5 if accumulated)
    protein_correct = "47" in json_str or "59.5" in json_str
    if protein_correct:
        score_details.append({"item": "Protein spending handled gracefully", "score": 15, "max_score": 15, "passed": True, "reason": "Calculated Protein costs handling the double-count (either deduplicated 47.0 or total 59.5)."})
        total_score += 15
    else:
        score_details.append({"item": "Protein spending handled gracefully", "score": 0, "max_score": 15, "passed": False, "reason": "Could not find expected Protein totals (47.0 or 59.5)."})

    # 5. Check Missing Ingredients
    # Should include Onions, Beef Stock, Baking Soda, Salt
    missing_items = find_val(json_data, ["missing", "ingredient", "need"])
    missing_str = json.dumps(missing_items).lower() if missing_items else json_str
    
    expected_missing = ["onion", "stock", "baking soda", "salt"]
    missing_found = [item for item in expected_missing if item in missing_str]
    
    if len(missing_found) == 4:
        score_details.append({"item": "Missing ingredients identified", "score": 25, "max_score": 25, "passed": True, "reason": "All missing ingredients (Onions, Beef Stock, Baking Soda, Salt) identified."})
        total_score += 25
    elif len(missing_found) > 0:
        partial_score = len(missing_found) * 5
        score_details.append({"item": "Missing ingredients identified", "score": partial_score, "max_score": 25, "passed": False, "reason": f"Only found partially: {missing_found}."})
        total_score += partial_score
    else:
        score_details.append({"item": "Missing ingredients identified", "score": 0, "max_score": 25, "passed": False, "reason": "Failed to identify the correct missing ingredients."})

    # 6. LLM Check for professionalism and no hallucination
    prompt = (
        "Check if this JSON output represents a professional inventory report. "
        "It MUST NOT hallucinate items that weren't in the receipts (e.g., no mention of organic saffron, hummingbirds feed, or car insurance). "
        "Does the report adhere to these constraints and omit irrelevant chaotic notes?"
    )
    if llm_judge_content(prompt, json.dumps(json_data)):
        score_details.append({"item": "LLM validation for professionalism and zero hallucination", "score": 15, "max_score": 15, "passed": True, "reason": "Passed LLM strict check."})
        total_score += 15
    else:
        score_details.append({"item": "LLM validation for professionalism and zero hallucination", "score": 0, "max_score": 15, "passed": False, "reason": "LLM detected hallucinations or lack of professionalism."})

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    verify()
