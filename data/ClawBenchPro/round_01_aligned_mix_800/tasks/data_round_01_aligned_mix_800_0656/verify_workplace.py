import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------------------------------------------------------
# Configuration & Constants
# ----------------------------------------------------------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize LLM Client
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

# Ground Truth for vintage items from the ledger:
# 1. 1950s workwear chore coat: $55.00
# 2. vintage silk tie: $18.50
# 3. 1970s flared corduroy pants: $22.75
# 4. vintage fedora hat: $40.00
# Total: 55.00 + 18.50 + 22.75 + 40.00 = 136.25

EXPECTED_ITEMS = [
    {"item": "1950s workwear chore coat", "cost": 55.00},
    {"item": "vintage silk tie", "cost": 18.50},
    {"item": "1970s flared corduroy pants", "cost": 22.75},
    {"item": "vintage fedora hat", "cost": 40.00}
]
EXPECTED_TOTAL = 136.25

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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = {"total_score": 0, "details": []}
    
    summary_dir = os.path.join(workspace, "summary")
    target_file = os.path.join(summary_dir, "clothing_expenses.json")

    # 1. Check Directory and File Existence (10 points)
    dir_exists = os.path.isdir(summary_dir)
    file_exists = os.path.isfile(target_file)
    score_1 = 10 if dir_exists and file_exists else 0
    results["details"].append({
        "item": "Directory and file existence (summary/clothing_expenses.json)",
        "score": score_1,
        "max_score": 10,
        "passed": score_1 == 10,
        "reason": "File found" if score_1 == 10 else "Required directory or file missing"
    })
    results["total_score"] += score_1

    if not file_exists:
        # Finalize and exit if the main file is missing
        with open("workplace_score.json", "w") as f:
            json.dump(results, f, indent=2)
        return

    # 2. JSON Format and Schema Validity (20 points)
    data = {}
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_2 = 20
        msg_2 = "JSON successfully parsed"
    except Exception as e:
        score_2 = 0
        msg_2 = f"Invalid JSON format: {str(e)}"
    
    results["details"].append({
        "item": "JSON Validity",
        "score": score_2,
        "max_score": 20,
        "passed": score_2 == 20,
        "reason": msg_2
    })
    results["total_score"] += score_2

    if score_2 == 0:
        with open("workplace_score.json", "w") as f:
            json.dump(results, f, indent=2)
        return

    # 3. Data Accuracy: Item Extraction and Filtering (40 points)
    # We check if exactly the 4 items are present and no "noise" items (groceries, fishing, bills)
    # This uses code-based logic for precision
    found_items = []
    # Try to find a list of items in the JSON. Be flexible with keys like "items", "expenses", etc.
    if isinstance(data, list):
        found_items = data
    elif isinstance(data, dict):
        for val in data.values():
            if isinstance(val, list):
                found_items = val
                break
    
    # Validation of items
    correct_count = 0
    noise_count = 0
    for item in found_items:
        desc = str(item).lower()
        # Positive Match
        if any(keyword in desc for keyword in ["coat", "tie", "pants", "hat", "fedora", "1950", "1970"]):
            correct_count += 1
        # Negative Match (Noise Check)
        if any(noise in desc for noise in ["groceries", "electric", "fishing", "prescription", "lures", "slaughterhouse"]):
            noise_count += 1

    # Scoring: 10 points per correct item (max 40), penalty for noise
    item_score = min(correct_count * 10, 40)
    if noise_count > 0:
        item_score = max(0, item_score - (noise_count * 10))
    
    results["details"].append({
        "item": "Data Extraction Accuracy (Correct items vs Noise)",
        "score": item_score,
        "max_score": 40,
        "passed": item_score == 40,
        "reason": f"Found {correct_count} correct items and {noise_count} noise items."
    })
    results["total_score"] += item_score

    # 4. Calculation Accuracy: Total Amount (20 points)
    # Agent must calculate $136.25
    agent_total = -1
    # Search for total in JSON
    if isinstance(data, dict):
        for k, v in data.items():
            if "total" in k.lower():
                try: agent_total = float(v)
                except: pass
    
    # Tolerance for float comparison
    calc_score = 0
    if abs(agent_total - EXPECTED_TOTAL) < 0.01:
        calc_score = 20
    
    results["details"].append({
        "item": "Calculation Accuracy (Total Amount)",
        "score": calc_score,
        "max_score": 20,
        "passed": calc_score == 20,
        "reason": f"Expected {EXPECTED_TOTAL}, found {agent_total}"
    })
    results["total_score"] += calc_score

    # 5. Quality & Conciseness (LLM Judge) (10 points)
    # Ensure the descriptions are clear and formatted properly for a spouse to see
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    prompt = "Is this JSON summary clear, clean, and specifically focused ONLY on vintage clothing expenses as requested by the worker? It should not contain internal rambling or system notes."
    is_good = llm_judge_content(prompt, content)
    llm_score = 10 if is_good else 0
    
    results["details"].append({
        "item": "LLM Quality Check (Formatting & Relevance)",
        "score": llm_score,
        "max_score": 10,
        "passed": llm_score == 10,
        "reason": "Passed LLM professional presentation check" if is_good else "Failed LLM quality check"
    })
    results["total_score"] += llm_score

    # Final Write
    with open("workplace_score.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
