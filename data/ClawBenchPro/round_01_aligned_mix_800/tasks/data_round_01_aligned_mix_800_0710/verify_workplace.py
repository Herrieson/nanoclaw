import os
import sys
import json
import httpx
from openai import OpenAI

# -----------------------------
# Configuration and API Setup
# -----------------------------
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
    """Fallback LLM validation for unstructured or semantic aspects (e.g., naming conventions)."""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[Content to Evaluate]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

# -----------------------------
# Helper Functions for Validation
# -----------------------------
def extract_keys(node, depth=0, max_depth=2):
    """Extracts top level keys to judge formatting professionalism."""
    keys = set()
    if depth > max_depth:
        return keys
    if isinstance(node, dict):
        for k, v in node.items():
            keys.add(str(k))
            keys.update(extract_keys(v, depth + 1, max_depth))
    elif isinstance(node, list):
        if len(node) > 0:
            keys.update(extract_keys(node[0], depth + 1, max_depth))
    return keys

def check_excluded(node, identifiers):
    """Deep search to ensure closed branch is totally purged."""
    if isinstance(node, dict):
        for k, v in node.items():
            if any(str(i).lower() in str(k).lower() for i in identifiers):
                return True
            if isinstance(v, str) and any(str(i).lower() in v.lower() for i in identifiers):
                return True
            if isinstance(v, (int, float)) and any(str(i) == str(v) for i in identifiers):
                return True
            if check_excluded(v, identifiers):
                return True
    elif isinstance(node, list):
        for item in node:
            if check_excluded(item, identifiers):
                return True
    return False

def search_for_branch(node, identifiers, expected_value, tolerance=5.0):
    """Robust deep search to map branch with its accurately calculated forecast."""
    def contains_target_value(n):
        if isinstance(n, dict):
            return any(contains_target_value(v) for v in n.values())
        elif isinstance(n, list):
            return any(contains_target_value(item) for item in n)
        elif isinstance(n, (int, float)):
            return abs(n - expected_value) <= tolerance
        elif isinstance(n, str):
            try:
                num = float(n.replace(',', '').replace('$', '').strip())
                return abs(num - expected_value) <= tolerance
            except:
                return False
        return False

    if isinstance(node, dict):
        is_match = False
        for k, v in node.items():
            if any(str(i).lower() in str(k).lower() for i in identifiers):
                is_match = True
                break
            if isinstance(v, str) and any(str(i).lower() in v.lower() for i in identifiers):
                is_match = True
                break
            if isinstance(v, (int, float)) and any(str(i) == str(v) for i in identifiers):
                is_match = True
                break
        
        if is_match:
            if contains_target_value(node):
                return True
        
        for v in node.values():
            if search_for_branch(v, identifiers, expected_value, tolerance):
                return True
                
    elif isinstance(node, list):
        for item in node:
            if search_for_branch(item, identifiers, expected_value, tolerance):
                return True
    return False

# -----------------------------
# Main Evaluation Logic
# -----------------------------
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "workspace", "q3_forecast_summary.json")
    
    score_details = []
    total_score = 0
    json_data = None
    
    # 1. Check File Existence and Validation (10 points)
    if not os.path.exists(target_file):
        score_details.append({"item": "Target JSON File Existence", "score": 0, "max_score": 10, "passed": False, "reason": "q3_forecast_summary.json not found."})
    else:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            score_details.append({"item": "Target JSON File Existence & Parse", "score": 10, "max_score": 10, "passed": True, "reason": "JSON structure perfectly loaded."})
            total_score += 10
        except json.JSONDecodeError:
            score_details.append({"item": "Target JSON File Existence & Parse", "score": 0, "max_score": 10, "passed": False, "reason": "File exists but is not valid JSON."})

    # Execute further checks only if JSON parsed properly
    if json_data is not None:
        
        # 2. Semantic LLM check of JSON Keys / Presentation (10 points)
        keys_set = extract_keys(json_data)
        if keys_set:
            keys_str = ", ".join(list(keys_set))
            prompt = "Are these JSON keys logically indicative of a financial forecast? They should reflect concepts like branch, ID, profit, projection, Q3, etc., instead of meaningless strings or completely empty datasets."
            is_professional = llm_judge_content(prompt, keys_str)
            if is_professional:
                score_details.append({"item": "Semantic Check of Data Keys", "score": 10, "max_score": 10, "passed": True, "reason": "LLM confirmed the structural keys are professionally appropriate."})
                total_score += 10
            else:
                score_details.append({"item": "Semantic Check of Data Keys", "score": 0, "max_score": 10, "passed": False, "reason": "LLM judged keys as unprofessional or irrelevant."})
        else:
            score_details.append({"item": "Semantic Check of Data Keys", "score": 0, "max_score": 10, "passed": False, "reason": "Failed to extract any keys. Dictionary/List may be empty."})

        # 3. Check dropping permanently closed branch 103 (15 points)
        has_103 = check_excluded(json_data, ["103", "Old Tavern Brooklyn"])
        if not has_103:
            score_details.append({"item": "Filter check: Closed branch excluded", "score": 15, "max_score": 15, "passed": True, "reason": "Branch 103 (Old Tavern Brooklyn) correctly omitted from output."})
            total_score += 15
        else:
            score_details.append({"item": "Filter check: Closed branch excluded", "score": 0, "max_score": 15, "passed": False, "reason": "Data from permanently closed branch 103 was incorrectly included."})

        # 4. Rigorous Mathematical Cross-Verification (65 points total)
        # Expected Logic: (Q1+Q2)/2 * rate * 1.05
        targets = [
            {"name": "Branch 101 (Paris)", "ids": ["101", "Le Bernardin Paris"], "val": 127050},
            {"name": "Branch 102 (London)", "ids": ["102", "Sushi Jiro London"], "val": 111562.5},
            {"name": "Branch 104 (Munich)", "ids": ["104", "Bavarian House Munich"], "val": 56595},
            {"name": "Branch 105 (NY)", "ids": ["105", "NY Prime Steakhouse"], "val": 162750},
            {"name": "Branch 106 (Tokyo)", "ids": ["106", "Tokyo Ramen"], "val": 40425}
        ]
        
        point_per_branch = 13
        for t in targets:
            if search_for_branch(json_data, t["ids"], t["val"], tolerance=5.0):
                score_details.append({"item": f"Accurate Projection: {t['name']}", "score": point_per_branch, "max_score": point_per_branch, "passed": True, "reason": "Forecast exactly matches mathematical expectation."})
                total_score += point_per_branch
            else:
                score_details.append({"item": f"Accurate Projection: {t['name']}", "score": 0, "max_score": point_per_branch, "passed": False, "reason": "Forecast is missing or computed incorrectly."})
    
    else:
        # Cascade failure for missing file
        score_details.append({"item": "Semantic Check of Data Keys", "score": 0, "max_score": 10, "passed": False, "reason": "JSON Parse failed."})
        score_details.append({"item": "Filter check: Closed branch excluded", "score": 0, "max_score": 15, "passed": False, "reason": "JSON Parse failed."})
        for branch_info in ["101", "102", "104", "105", "106"]:
            score_details.append({"item": f"Accurate Projection: Branch {branch_info}", "score": 0, "max_score": 13, "passed": False, "reason": "JSON Parse failed."})

    # Wrap up result
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
