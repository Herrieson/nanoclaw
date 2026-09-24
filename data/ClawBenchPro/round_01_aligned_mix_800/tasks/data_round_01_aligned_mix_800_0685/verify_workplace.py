import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# Configuration for LLM if needed (though this task is mostly deterministic)
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def calculate_expected():
    """
    Logic:
    1. Traditional_Lechon: 3*3.0 + 5*0.1 + 2*0.2 = 9.0 + 0.5 + 0.4 = 9.9. Carbon: 3*10+5*0.1+2*0.2 = 30.9
    2. Eco_Plantain_Bowl: 4*0.5 + 3*0.2 + 2*0.3 + 1*2.5 = 2.0 + 0.6 + 0.6 + 2.5 = 5.7. Carbon: 4*1.0+3*0.5+2*1.2+1*2.0 = 4.0+1.5+2.4+2.0 = 9.9
    3. Fancy_Paella: 5*4.0 + 3*0.3 + 1*10.0 = 20 + 0.9 + 10 = 30.9 (Over budget $15)
    4. Chicken_Mojo: 3*2.0 + 4*0.1 + 2*0.2 + 2*0.3 = 6.0 + 0.4 + 0.4 + 0.6 = 7.4. Carbon: 3*5+4*0.1+2*0.2+2*1.2 = 15+0.4+0.4+2.4 = 18.2

    Valid under $15: Lechon ($9.9, Carbon 30.9), Eco Bowl ($5.7, Carbon 9.9), Chicken Mojo ($7.4, Carbon 18.2).
    Winner (Lowest Carbon): Eco_Plantain_Bowl (Carbon 9.9).
    """
    return {
        "name": "Eco_Plantain_Bowl",
        "cost": 5.7,
        "carbon": 9.9,
        "ingredients": ["Plantain", "BlackBeans", "Rice", "OrganicAvocado"]
    }

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = os.path.join(workspace, "workplace_score.json")
    target_path = os.path.join(workspace, "kitchen_prep/winning_recipe_order.json")
    
    score = 0
    details = []

    # 1. Directory & File Existence (10 points)
    if os.path.exists(target_path):
        score += 10
        details.append({"item": "File existence", "score": 10, "max_score": 10, "passed": True, "reason": "winning_recipe_order.json found"})
    else:
        details.append({"item": "File existence", "score": 0, "max_score": 10, "passed": False, "reason": "winning_recipe_order.json not found"})
        # Write 0 and exit if file is missing
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 2. JSON Validity & Schema (20 points)
    try:
        with open(target_path, 'r') as f:
            data = json.load(f)
        score += 20
        details.append({"item": "JSON format", "score": 20, "max_score": 20, "passed": True, "reason": "JSON is valid and loadable"})
    except Exception as e:
        details.append({"item": "JSON format", "score": 0, "max_score": 20, "passed": False, "reason": f"Failed to parse JSON: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    expected = calculate_expected()

    # 3. Correct Recipe Identification (30 points)
    # The winner must be Eco_Plantain_Bowl
    actual_name = data.get("name", "") or data.get("recipe_name", "")
    if "Eco_Plantain_Bowl" in str(actual_name):
        score += 30
        details.append({"item": "Winner identification", "score": 30, "max_score": 30, "passed": True, "reason": "Correct recipe identified"})
    else:
        details.append({"item": "Winner identification", "score": 0, "max_score": 30, "passed": False, "reason": f"Incorrect winner. Expected Eco_Plantain_Bowl, got {actual_name}"})

    # 4. Accurate Calculation: Cost & Carbon (30 points)
    # Allow small float delta
    try:
        actual_cost = float(data.get("total_cost", 0))
        actual_carbon = float(data.get("total_carbon_footprint", 0))
        
        cost_ok = abs(actual_cost - expected["cost"]) < 0.01
        carbon_ok = abs(actual_carbon - expected["carbon"]) < 0.01
        
        if cost_ok and carbon_ok:
            score += 30
            details.append({"item": "Calculation accuracy", "score": 30, "max_score": 30, "passed": True, "reason": f"Cost ({actual_cost}) and Carbon ({actual_carbon}) are precise"})
        elif cost_ok or carbon_ok:
            score += 15
            details.append({"item": "Calculation accuracy", "score": 15, "max_score": 30, "passed": False, "reason": f"Partial match. Cost correct: {cost_ok}, Carbon correct: {carbon_ok}"})
        else:
            details.append({"item": "Calculation accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "Both cost and carbon calculations are incorrect"})
    except:
        details.append({"item": "Calculation accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "Could not extract numeric cost/carbon from JSON"})

    # 5. Ingredient List (10 points)
    actual_ingredients = data.get("ingredients", [])
    if isinstance(actual_ingredients, list) and all(ing in str(actual_ingredients) for ing in expected["ingredients"]):
        score += 10
        details.append({"item": "Ingredient list", "score": 10, "max_score": 10, "passed": True, "reason": "All required ingredients listed"})
    else:
        details.append({"item": "Ingredient list", "score": 0, "max_score": 10, "passed": False, "reason": "Ingredient list is missing or incomplete"})

    # Final Output
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(score), "details": details}, f)

if __name__ == "__main__":
    verify()
