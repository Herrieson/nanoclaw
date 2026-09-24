import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------------------------------------------------------
# Configuration & LLM Setup
# ----------------------------------------------------------------
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

# ----------------------------------------------------------------
# Validation Logic
# ----------------------------------------------------------------
def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables", "best_recipe.json")
    
    details = []
    total_score = 0

    # 1. Check File Existence (10 points)
    if os.path.exists(deliverables_path):
        score = 10
        passed = True
        reason = "deliverables/best_recipe.json exists."
    else:
        details.append({"item": "File Existence", "score": 0, "max_score": 10, "passed": False, "reason": "best_recipe.json not found."})
        # If file missing, return early
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    total_score += score
    details.append({"item": "File Existence", "score": 10, "max_score": 10, "passed": True, "reason": reason})

    # 2. Schema Validation (20 points)
    try:
        with open(deliverables_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        required_keys = ["name", "score", "ingredients"]
        missing_keys = [k for k in required_keys if k not in data]
        
        if not missing_keys:
            total_score += 20
            details.append({"item": "JSON Schema", "score": 20, "max_score": 20, "passed": True, "reason": "All required keys present."})
        else:
            details.append({"item": "JSON Schema", "score": 0, "max_score": 20, "passed": False, "reason": f"Missing keys: {missing_keys}"})
    except Exception as e:
        details.append({"item": "JSON Parsing", "score": 0, "max_score": 20, "passed": False, "reason": f"Parsing error: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    # 3. Accuracy of Selection (50 points)
    # Target Logic: 
    # A (80mV->pH 5.4, score 9.2, Natural) - OK
    # B (10mV->pH 6.8, score 8.5, Natural) - WRONG pH
    # C (75mV->pH 5.5, score 9.6, Synthetic: Dimethicone) - WRONG Ingredient
    # D (90mV->pH 5.2, score 9.4, Natural) - OK
    # Best is D (Aloe Soothe, Score 9.4)
    
    target_name = "Aloe Soothe"
    if data.get("name") == target_name:
        total_score += 50
        details.append({"item": "Optimal Selection", "score": 50, "max_score": 50, "passed": True, "reason": "Correctly identified Aloe Soothe as the highest scoring natural recipe with valid pH."})
    elif data.get("name") == "Lavender Dream":
        total_score += 20
        details.append({"item": "Optimal Selection", "score": 20, "max_score": 50, "passed": False, "reason": "Selected a valid recipe (Lavender Dream), but not the one with the highest score."})
    elif data.get("name") == "Rose Smooth":
        details.append({"item": "Optimal Selection", "score": 0, "max_score": 50, "passed": False, "reason": "Failed: Rose Smooth contains Dimethicone (Synthetic)."})
    else:
        details.append({"item": "Optimal Selection", "score": 0, "max_score": 50, "passed": False, "reason": f"Incorrect selection: {data.get('name')}"})

    # 4. Accuracy of Data Extraction (20 points)
    # Check if the score and ingredients in the JSON match the raw file
    raw_score = 9.4
    raw_ingredients = ["Aloe Vera", "Shea Butter", "Beeswax"]
    
    extracted_score = data.get("score")
    extracted_ingredients = data.get("ingredients", [])
    
    score_match = (float(extracted_score) == raw_score) if extracted_score else False
    # Use LLM to verify ingredient list semantic match to avoid ordering/formatting issues
    ingredient_prompt = f"Does this list of ingredients match exactly: {raw_ingredients}?"
    ingredients_match = llm_judge_content(ingredient_prompt, str(extracted_ingredients))
    
    if score_match and ingredients_match:
        total_score += 20
        details.append({"item": "Data Integrity", "score": 20, "max_score": 20, "passed": True, "reason": "Score and ingredients match the source records."})
    else:
        reason = []
        if not score_match: reason.append("Score mismatch")
        if not ingredients_match: reason.append("Ingredients list mismatch")
        details.append({"item": "Data Integrity", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(reason)})

    # Final output
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(total_score), "details": details}, f)

if __name__ == "__main__":
    run_verification()
