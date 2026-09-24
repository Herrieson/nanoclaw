#!/usr/bin/env python3
import os
import sys
import json
import httpx
from openai import OpenAI

# ---------------------------------------------------------
# Environment & LLM Client Setup
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# Helper Functions for Strict Deterministic Parsing
# ---------------------------------------------------------
def find_key_value_fuzzy(obj, target_key_substring, target_value):
    """Recursively search for a key containing a substring whose value matches the target (for floats)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if target_key_substring.lower() in k.lower():
                if isinstance(v, (int, float)) and abs(v - target_value) < 0.01:
                    return True
            if find_key_value_fuzzy(v, target_key_substring, target_value):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if find_key_value_fuzzy(item, target_key_substring, target_value):
                return True
    return False

def find_value_in_json(obj, target_value_check_fn):
    """Recursively search for a value that passes the check function."""
    if isinstance(obj, dict):
        for v in obj.values():
            if target_value_check_fn(v) or find_value_in_json(v, target_value_check_fn):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if target_value_check_fn(item) or find_value_in_json(item, target_value_check_fn):
                return True
    return False

# ---------------------------------------------------------
# Main Verification Logic
# ---------------------------------------------------------
def verify(workspace_path):
    deliverables_dir = os.path.join(workspace_path, "deliverables")
    plan_file = os.path.join(deliverables_dir, "shopping_plan.json")
    
    details = []
    total_score = 0
    
    # 1. Structure Check (10 points)
    has_dir = os.path.isdir(deliverables_dir)
    has_file = os.path.isfile(plan_file)
    valid_json = False
    plan_data = None
    
    if has_file:
        try:
            with open(plan_file, "r", encoding="utf-8") as f:
                plan_data = json.load(f)
            valid_json = True
        except json.JSONDecodeError:
            pass
            
    if valid_json:
        details.append({"item": "Deliverables & JSON Schema", "score": 10, "max_score": 10, "passed": True, "reason": "Valid shopping_plan.json found."})
        total_score += 10
    else:
        details.append({"item": "Deliverables & JSON Schema", "score": 0, "max_score": 10, "passed": False, "reason": "Missing directory, file, or invalid JSON format."})

    # If JSON is invalid, the rest of the deterministic checks fail automatically.
    if not valid_json:
        # Fill remaining with 0
        details.extend([
            {"item": "Allergy Substitution", "score": 0, "max_score": 20, "passed": False, "reason": "Cannot parse JSON."},
            {"item": "Ingredient Quantities", "score": 0, "max_score": 30, "passed": False, "reason": "Cannot parse JSON."},
            {"item": "Store Selection", "score": 0, "max_score": 15, "passed": False, "reason": "Cannot parse JSON."},
            {"item": "Total Cost Math", "score": 0, "max_score": 15, "passed": False, "reason": "Cannot parse JSON."},
            {"item": "Persona & Semantic Context", "score": 0, "max_score": 10, "passed": False, "reason": "Cannot parse JSON."}
        ])
    else:
        # Stringified JSON for global structural checks
        data_str = json.dumps(plan_data).lower()
        
        # 2. Allergy Substitution (20 points)
        # MUST contain canola oil and MUST NOT contain peanut oil
        has_canola = "canola" in data_str
        has_peanut = "peanut" in data_str
        
        if has_canola and not has_peanut:
            details.append({"item": "Allergy Substitution", "score": 20, "max_score": 20, "passed": True, "reason": "Successfully swapped peanut oil to canola oil."})
            total_score += 20
        elif has_canola and has_peanut:
            details.append({"item": "Allergy Substitution", "score": 5, "max_score": 20, "passed": False, "reason": "Added canola oil but failed to remove peanut oil (Critical allergy risk!)."})
            total_score += 5
        else:
            details.append({"item": "Allergy Substitution", "score": 0, "max_score": 20, "passed": False, "reason": "Failed to handle peanut allergy constraint."})

        # 3. Ingredient Quantities (30 points)
        # Checking a sample of critical math (10 portions total)
        has_tomatoes = find_key_value_fuzzy(plan_data, "tomato", 5.0)
        has_onions = find_key_value_fuzzy(plan_data, "onion", 2.5)
        has_chicken = find_key_value_fuzzy(plan_data, "chicken", 4.0)
        
        ing_score = 0
        ing_passed = False
        ing_reason = []
        if has_tomatoes: ing_score += 10; ing_reason.append("Tomatoes correct (5.0)")
        if has_onions: ing_score += 10; ing_reason.append("Onions correct (2.5)")
        if has_chicken: ing_score += 10; ing_reason.append("Chicken correct (4.0)")
        
        if ing_score == 30: ing_passed = True
        details.append({"item": "Ingredient Quantities", "score": ing_score, "max_score": 30, "passed": ing_passed, "reason": ", ".join(ing_reason) if ing_reason else "Failed to calculate 10 portions correctly."})
        total_score += ing_score

        # 4. Store Selection (15 points)
        def check_store(val):
            return isinstance(val, str) and "atlanta international market" in val.lower()
            
        store_correct = find_value_in_json(plan_data, check_store)
        if store_correct:
            details.append({"item": "Store Selection", "score": 15, "max_score": 15, "passed": True, "reason": "Correctly identified Atlanta International Market."})
            total_score += 15
        else:
            details.append({"item": "Store Selection", "score": 0, "max_score": 15, "passed": False, "reason": "Failed to select the correct cheapest store."})

        # 5. Total Cost Math (15 points)
        # Expected exact cost is 34.5 (or 34.50)
        def check_cost(val):
            return isinstance(val, (int, float)) and abs(val - 34.5) < 0.01
            
        cost_correct = find_value_in_json(plan_data, check_cost)
        if cost_correct:
            details.append({"item": "Total Cost Math", "score": 15, "max_score": 15, "passed": True, "reason": "Correctly calculated total price of $34.50."})
            total_score += 15
        else:
            details.append({"item": "Total Cost Math", "score": 0, "max_score": 15, "passed": False, "reason": "Final cost calculation is incorrect (Expected 34.50)."})

        # 6. Persona & Semantic Context via LLM (10 points)
        # Check if the JSON includes any note, summary, or keys that acknowledge Marcus's context (factory work, cookout, safety).
        prompt = (
            "Does the following JSON content include a friendly note, message, or specific descriptive keys "
            "that acknowledge the user's specific context (e.g., mentioning 'Marcus', 'cookout', 'factory', 'safety', or wishing them a good time)? "
            "Look for conversational elements embedded in the JSON structure. If yes, say YES. If it's just raw data without context, say NO."
        )
        has_persona = llm_judge_content(prompt, json.dumps(plan_data, indent=2))
        
        if has_persona:
            details.append({"item": "Persona & Semantic Context", "score": 10, "max_score": 10, "passed": True, "reason": "LLM verified persona acknowledgement in the report."})
            total_score += 10
        else:
            details.append({"item": "Persona & Semantic Context", "score": 0, "max_score": 10, "passed": False, "reason": "Missing personalized message or context for Marcus in the output."})

    # Write output
    output = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
