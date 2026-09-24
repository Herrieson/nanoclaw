import os
import sys
import json
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables", "best_recipe.json")
    score_file = "workplace_score.json"
    
    details = []
    total_score = 0

    # 1. Check file existence (10 points)
    if os.path.exists(deliverables_path):
        details.append({"item": "Check deliverables/best_recipe.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found."})
        total_score += 10
        
        # 2. Schema and Content Validation (Code-based)
        try:
            with open(deliverables_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check mandatory fields (15 points)
            required_keys = ["Recipe Name", "Score", "Ingredients list"]
            missing_keys = [k for k in required_keys if k not in data]
            if not missing_keys:
                details.append({"item": "JSON Schema Validation", "score": 15, "max_score": 15, "passed": True, "reason": "All required keys present."})
                total_score += 15
            else:
                details.append({"item": "JSON Schema Validation", "score": 0, "max_score": 15, "passed": False, "reason": f"Missing keys: {missing_keys}"})

            # 3. Accuracy Check - The specific winner (50 points)
            # The winner defined in env_builder is: Project_Phoenix_Final, Score 9.8, 
            # Ingredients: ["Lavender Oil", "Shea Butter", "Honey"]
            correct_name = "Project_Phoenix_Final"
            correct_score = 9.8
            correct_ingredients = ["Lavender Oil", "Shea Butter", "Honey"]

            # Name Check (10 points)
            if data.get("Recipe Name") == correct_name:
                details.append({"item": "Correct Recipe Name identified", "score": 10, "max_score": 10, "passed": True, "reason": "Matched 'Project_Phoenix_Final'"})
                total_score += 10
            else:
                details.append({"item": "Correct Recipe Name identified", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {correct_name}, got {data.get('Recipe Name')}"})

            # Score Check (20 points)
            try:
                if abs(float(data.get("Score", 0)) - correct_score) < 0.01:
                    details.append({"item": "Correct Efficacy Score", "score": 20, "max_score": 20, "passed": True, "reason": "Score matches 9.8"})
                    total_score += 20
                else:
                    details.append({"item": "Correct Efficacy Score", "score": 0, "max_score": 20, "passed": False, "reason": f"Score {data.get('Score')} is incorrect."})
            except:
                details.append({"item": "Correct Efficacy Score", "score": 0, "max_score": 20, "passed": False, "reason": "Score is not a valid number."})

            # Ingredients Check (20 points)
            user_ingredients = [str(i).strip().lower() for i in data.get("Ingredients list", [])]
            target_ingredients = [i.lower() for i in correct_ingredients]
            if set(user_ingredients) == set(target_ingredients):
                details.append({"item": "Correct Ingredients List", "score": 20, "max_score": 20, "passed": True, "reason": "Ingredients match requirements."})
                total_score += 20
            else:
                details.append({"item": "Correct Ingredients List", "score": 0, "max_score": 20, "passed": False, "reason": "Ingredients list mismatch."})

            # 4. Logical Integrity - LLM Validation (25 points)
            # Check if the ingredients are actually 'Natural' based on the archive
            # This prevents Agent from hallucinating or picking a high score with synthetic ingredients
            llm_prompt = """
            Verify if the following ingredient list consists ONLY of natural ingredients based on typical lab standards. 
            Also, confirm if the ingredients listed match the specific high-end recipe 'Project_Phoenix_Final' mentioned in the context.
            Respond only with 'YES' if it's natural and correct, or 'NO' if it contains synthetics like Dimethicone, Parabens, or Phthalates.
            """
            
            MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
            MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
            MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

            try:
                http_client = httpx.Client(verify=False)
                client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
                response = client.chat.completions.create(
                    model=MOCK_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "You are a strict chemical safety auditor. Answer ONLY 'YES' or 'NO'."},
                        {"role": "user", "content": f"{llm_prompt}\n\n[Ingredients]: {data.get('Ingredients list')}"}
                    ],
                    temperature=0
                )
                if "yes" in response.choices[0].message.content.strip().lower():
                    details.append({"item": "LLM Verification: Purity & Relevance", "score": 25, "max_score": 25, "passed": True, "reason": "LLM confirms ingredients are natural and relevant."})
                    total_score += 25
                else:
                    details.append({"item": "LLM Verification: Purity & Relevance", "score": 0, "max_score": 25, "passed": False, "reason": "LLM flagged potential synthetic ingredients or incorrect formula."})
            except Exception as e:
                # Fallback for connectivity issues: check against forbidden list manually
                forbidden = ["dimethicone", "parabens", "phthalates", "sodium lauryl sulfate", "petrolatum"]
                if not any(f in str(user_ingredients) for f in forbidden):
                    details.append({"item": "Manual Ingredient Safety Check (LLM Fallback)", "score": 25, "max_score": 25, "passed": True, "reason": "No common synthetics found."})
                    total_score += 25
                else:
                    details.append({"item": "Manual Ingredient Safety Check (LLM Fallback)", "score": 0, "max_score": 25, "passed": False, "reason": "Synthetics detected."})

        except Exception as e:
            details.append({"item": "Data Parsing Error", "score": 0, "max_score": 90, "passed": False, "reason": str(e)})

    else:
        details.append({"item": "Check deliverables/best_recipe.json exists", "score": 0, "max_score": 100, "passed": False, "reason": "Deliverable file not found."})

    with open(score_file, 'w') as f:
        json.dump({"total_score": int(total_score), "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
