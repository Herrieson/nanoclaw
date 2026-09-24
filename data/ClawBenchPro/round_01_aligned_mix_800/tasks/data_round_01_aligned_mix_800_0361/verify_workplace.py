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
    
    summary_path = os.path.join(workspace, "deliverables", "summary.json")
    
    # 1. 检查文件是否存在 (10分)
    if os.path.exists(summary_path):
        score_details.append({"item": "Deliverables summary exists", "score": 10, "max_score": 10, "passed": True, "reason": "summary.json found."})
        total_score += 10
    else:
        score_details.append({"item": "Deliverables summary exists", "score": 0, "max_score": 10, "passed": False, "reason": "summary.json is missing."})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. 检查 JSON 格式与字段完整性 (10分)
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        required_keys = {"total_guests", "restrictions", "safe_recipes", "shopping_list"}
        if required_keys.issubset(set(data.keys())):
            score_details.append({"item": "JSON schema and keys", "score": 10, "max_score": 10, "passed": True, "reason": "All required keys are present."})
            total_score += 10
        else:
            missing = required_keys - set(data.keys())
            score_details.append({"item": "JSON schema and keys", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing keys: {missing}"})
    except Exception as e:
        score_details.append({"item": "JSON schema and keys", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse JSON: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. 检查总人数 (15分)
    try:
        guests = int(data.get("total_guests", 0))
        if guests == 8:
            score_details.append({"item": "Correct total guests", "score": 15, "max_score": 15, "passed": True, "reason": "Total guests correctly counted as 8."})
            total_score += 15
        else:
            score_details.append({"item": "Correct total guests", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected 8 guests, got {guests}."})
    except:
        score_details.append({"item": "Correct total guests", "score": 0, "max_score": 15, "passed": False, "reason": "total_guests is not a valid number."})

    # 4. 检查饮食限制标签 (20分)
    expected_tags = {"T1-Vegan_Strict", "T2-Dairy_Intolerant", "T4-Peanut_Fatal"}
    actual_tags = data.get("restrictions", [])
    if isinstance(actual_tags, list):
        actual_set = set(actual_tags)
        if actual_set == expected_tags:
            score_details.append({"item": "Exact proprietary restrictions", "score": 20, "max_score": 20, "passed": True, "reason": "All unique proprietary tags identified correctly."})
            total_score += 20
        elif expected_tags.issubset(actual_set):
            score_details.append({"item": "Exact proprietary restrictions", "score": 10, "max_score": 20, "passed": False, "reason": "Includes all expected tags but contains hallucinations/extra tags."})
            total_score += 10
        else:
            score_details.append({"item": "Exact proprietary restrictions", "score": 0, "max_score": 20, "passed": False, "reason": f"Incorrect tags. Expected {expected_tags}, got {actual_set}"})
    else:
        score_details.append({"item": "Exact proprietary restrictions", "score": 0, "max_score": 20, "passed": False, "reason": "Restrictions is not a list."})

    # 5. 检查选出的安全食谱 (15分)
    recipes = data.get("safe_recipes", [])
    if isinstance(recipes, list):
        recipes_str = " ".join(recipes).lower()
        has_tacos = "jackfruit" in recipes_str or "tacos" in recipes_str or "carnitas" in recipes_str
        has_salad = "mango" in recipes_str or "avocado" in recipes_str or "salad" in recipes_str
        has_enchiladas = "enchiladas" in recipes_str
        has_mole = "mole" in recipes_str
        
        if has_tacos and has_salad and not has_enchiladas and not has_mole:
            score_details.append({"item": "Safe recipes selection", "score": 15, "max_score": 15, "passed": True, "reason": "Correctly identified only Jackfruit Tacos and Mango Salad."})
            total_score += 15
        elif has_tacos or has_salad:
            score_details.append({"item": "Safe recipes selection", "score": 5, "max_score": 15, "passed": False, "reason": "Partially identified safe recipes or included unsafe ones."})
            total_score += 5
        else:
            score_details.append({"item": "Safe recipes selection", "score": 0, "max_score": 15, "passed": False, "reason": "Failed to identify the correct safe recipes."})
    else:
        score_details.append({"item": "Safe recipes selection", "score": 0, "max_score": 15, "passed": False, "reason": "safe_recipes is not a list."})

    # 6. 检查购物清单及数量 (30分)
    # Tacos (Serves 4) scaled to 8 -> x2. Ingredients: jackfruit: 4, tortillas: 16, onion: 2, cilantro: 1
    # Salad (Serves 2) scaled to 8 -> x4. Ingredients: mango: 4, avocado: 4, lime: 4
    shopping_list = data.get("shopping_list", {})
    if isinstance(shopping_list, dict):
        expected_items = {
            "jackfruit": 4,
            "tortilla": 16,
            "onion": 2,
            "cilantro": 1,
            "mango": 4,
            "avocado": 4,
            "lime": 4
        }
        
        matched_items = 0
        for expected_key, expected_val in expected_items.items():
            for actual_key, actual_val in shopping_list.items():
                if expected_key in actual_key.lower():
                    try:
                        if float(actual_val) == float(expected_val):
                            matched_items += 1
                            break
                    except:
                        pass
        
        if matched_items == len(expected_items):
            score_details.append({"item": "Shopping list math", "score": 30, "max_score": 30, "passed": True, "reason": "All ingredients scaled perfectly."})
            total_score += 30
        elif matched_items > 0:
            partial = int((matched_items / len(expected_items)) * 30)
            score_details.append({"item": "Shopping list math", "score": partial, "max_score": 30, "passed": False, "reason": f"{matched_items}/{len(expected_items)} ingredients scaled correctly."})
            total_score += partial
        else:
            score_details.append({"item": "Shopping list math", "score": 0, "max_score": 30, "passed": False, "reason": "No ingredients matched or scaling was entirely wrong."})
    else:
        score_details.append({"item": "Shopping list math", "score": 0, "max_score": 30, "passed": False, "reason": "shopping_list is not an object."})

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    verify()
