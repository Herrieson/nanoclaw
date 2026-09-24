import os
import sys
import json
import csv
import glob
import httpx
from openai import OpenAI

# Configuration for potential LLM usage
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

def calculate_ground_truth(workspace):
    # Replicate logic from env_builder to get ground truth
    schema_path = os.path.join(workspace, "raw_archives/manifest_schema_v2.json")
    if not os.path.exists(schema_path):
        return None, None
    
    with open(schema_path, "r") as f:
        schema = json.load(f)
    
    valid_prefixes = schema["valid_prefixes"]
    target_categories = schema["target_categories"]
    status_flag = schema["status_flag"]

    total_spent = {cat: 0.0 for cat in target_categories}
    acquired_items = set()

    # Sector Alpha (CSV)
    alpha_files = glob.glob(os.path.join(workspace, "raw_archives/sector_alpha/logs/*.csv"))
    for fpath in alpha_files:
        fname = os.path.basename(fpath)
        if any(fname.startswith(p) for p in valid_prefixes):
            with open(fpath, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["status"] == status_flag:
                        cat = row["category"]
                        if cat in target_categories:
                            cost = float(row["cost"])
                            qty = int(row["quantity"])
                            total_spent[cat] += cost * qty
                            acquired_items.add(row["item_name"])

    # Sector Beta (JSON)
    beta_files = glob.glob(os.path.join(workspace, "raw_archives/sector_beta/temp/*.json"))
    for fpath in beta_files:
        fname = os.path.basename(fpath)
        if any(fname.startswith(p) for p in valid_prefixes):
            with open(fpath, "r") as f:
                data = json.load(f)
                entry = data.get("entry", {})
                if entry.get("auth_code") == status_flag:
                    cat = entry.get("group")
                    if cat in target_categories:
                        cost = entry["pricing"]["amt"]
                        qty = entry["count"]
                        total_spent[cat] += cost * qty
                        acquired_items.add(entry["label"])

    # Missing Items
    recipe_path = os.path.join(workspace, "recipes_logic/active_requirements.json")
    missing_items = {}
    if os.path.exists(recipe_path):
        with open(recipe_path, "r") as f:
            recipes = json.load(f)
            for r_name, ingredients in recipes.items():
                missing = [ing for ing in ingredients if ing not in acquired_items]
                missing_items[r_name] = missing

    return total_spent, missing_items

def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = os.path.join(workspace, "pantry_audit/summary.json")
    score_details = []
    total_score = 0

    # 1. Check if output file exists (10 points)
    if os.path.exists(output_file):
        score_details.append({"item": "Existence of summary.json", "score": 10, "max_score": 10, "passed": True, "reason": "Found output file."})
        total_score += 10
    else:
        score_details.append({"item": "Existence of summary.json", "score": 0, "max_score": 10, "passed": False, "reason": "summary.json not found."})
        # If missing, we can't check contents, but let's continue for partials if directory exists
    
    # Calculate Ground Truth
    gt_spent, gt_missing = calculate_ground_truth(workspace)
    if gt_spent is None:
        # This shouldn't happen if env is built correctly
        print("Error: Ground truth could not be established.")
        sys.exit(1)

    # 2. Check content of summary.json
    if os.path.exists(output_file):
        try:
            with open(output_file, "r") as f:
                agent_data = json.load(f)
            
            # Check categories aggregation (50 points)
            spent_match_count = 0
            for cat in gt_spent:
                # Use small epsilon for float comparison
                agent_val = agent_data.get("total_spent", {}).get(cat, -1)
                if abs(agent_val - gt_spent[cat]) < 0.1:
                    spent_match_count += 1
            
            cat_score = int((spent_match_count / len(gt_spent)) * 50)
            score_details.append({
                "item": "Financial Reconcilliation (Total Spent)",
                "score": cat_score,
                "max_score": 50,
                "passed": cat_score == 50,
                "reason": f"Matched {spent_match_count}/{len(gt_spent)} target categories correctly."
            })
            total_score += cat_score

            # Check Missing Ingredients (30 points)
            missing_match_count = 0
            agent_missing = agent_data.get("missing_items", {})
            for recipe, ingredients in gt_missing.items():
                agent_ing = agent_missing.get(recipe, [])
                if set(agent_ing) == set(ingredients):
                    missing_match_count += 1
            
            missing_score = int((missing_match_count / len(gt_missing)) * 30)
            score_details.append({
                "item": "Missing Ingredient Analysis",
                "score": missing_score,
                "max_score": 30,
                "passed": missing_score == 30,
                "reason": f"Matched {missing_match_count}/{len(gt_missing)} recipe audits."
            })
            total_score += missing_score

            # Check Format/Cleanup (10 points)
            # Ensure no 'Waste' or 'Industrial' categories are in the total_spent
            if all(k in gt_spent for k in agent_data.get("total_spent", {}).keys()):
                score_details.append({"item": "Data Filtering Quality", "score": 10, "max_score": 10, "passed": True, "reason": "No extraneous categories found."})
                total_score += 10
            else:
                score_details.append({"item": "Data Filtering Quality", "score": 0, "max_score": 10, "passed": False, "reason": "Included non-target or trash categories."})

        except Exception as e:
            score_details.append({"item": "JSON Parsing/Logic Error", "score": 0, "max_score": 90, "passed": False, "reason": str(e)})

    # Final Summary
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    run_verification()
