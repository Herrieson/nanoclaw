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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "kitchen_prep", "winning_recipe_order.json")
    
    total_score = 0
    details = []

    # 1. 检查文件是否存在 (10分)
    if not os.path.exists(target_file):
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 winning_recipe_order.json 文件"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2)
        return
    else:
        details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10

    # 2. 检查 JSON 格式是否合法 (10分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content_str = f.read()
            data = json.loads(content_str)
        details.append({"item": "检查 JSON 格式", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON 格式"})
        total_score += 10
    except json.JSONDecodeError:
        details.append({"item": "检查 JSON 格式", "score": 0, "max_score": 10, "passed": False, "reason": "文件无法解析为合法的 JSON"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 检查必要字段完整性 (10分)
    required_keys = {"recipe_name", "total_cost", "total_carbon_footprint", "ingredient_list"}
    missing_keys = required_keys - set(data.keys())
    if missing_keys:
        details.append({"item": "检查 JSON 字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段: {', '.join(missing_keys)}"})
    else:
        details.append({"item": "检查 JSON 字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所有必要字段均存在"})
        total_score += 10

    if not missing_keys:
        # 4. 检查食谱名称 (20分)
        if data["recipe_name"] == "Eco_Plantain_Bowl":
            details.append({"item": "检查最终选择的食谱名称", "score": 20, "max_score": 20, "passed": True, "reason": "正确选出碳排最低且不超预算的食谱"})
            total_score += 20
        else:
            details.append({"item": "检查最终选择的食谱名称", "score": 0, "max_score": 20, "passed": False, "reason": f"选出的食谱错误: {data.get('recipe_name')}"})

        # 5. 检查总价计算是否精准 (15分)
        try:
            cost = float(data["total_cost"])
            if abs(cost - 5.7) < 0.01:
                details.append({"item": "检查总价计算结果", "score": 15, "max_score": 15, "passed": True, "reason": "总价精确匹配 5.7"})
                total_score += 15
            else:
                details.append({"item": "检查总价计算结果", "score": 0, "max_score": 15, "passed": False, "reason": f"总价计算错误: {cost} (预期 5.7)"})
        except ValueError:
            details.append({"item": "检查总价计算结果", "score": 0, "max_score": 15, "passed": False, "reason": "总价包含无法转换为浮点数的无效字符"})

        # 6. 检查碳足迹计算是否精准 (15分)
        try:
            carbon = float(data["total_carbon_footprint"])
            if abs(carbon - 9.9) < 0.01:
                details.append({"item": "检查碳排计算结果", "score": 15, "max_score": 15, "passed": True, "reason": "碳足迹精确匹配 9.9"})
                total_score += 15
            else:
                details.append({"item": "检查碳排计算结果", "score": 0, "max_score": 15, "passed": False, "reason": f"碳足迹计算错误: {carbon} (预期 9.9)"})
        except ValueError:
            details.append({"item": "检查碳排计算结果", "score": 0, "max_score": 15, "passed": False, "reason": "碳足迹包含无法转换为浮点数的无效字符"})

        # 7. 检查 ingredient_list 数据内容与形式 (20分)
        ing_list = data["ingredient_list"]
        ing_list_str = json.dumps(ing_list)
        
        # 使用 LLM 辅助检查非结构化形式或嵌套结构中的名称是否清晰合规且无冗余
        prompt = "Does the following JSON representation of an ingredient list exclusively contain 'Plantain', 'BlackBeans', 'Rice', and 'OrganicAvocado' with their respective quantities or structures, absolutely WITHOUT using alias names like 'Starch_Stick' or 'Green_Gold', and completely FREE from unrelated ingredients like 'Chicken' or 'Shrimp'?"
        is_clean = llm_judge_content(prompt, ing_list_str)
        
        has_correct_names = all(item in ing_list_str for item in ["Plantain", "BlackBeans", "Rice", "OrganicAvocado"])
        has_aliases = any(item in ing_list_str for item in ["Starch_Stick", "Green_Gold", "Protein_P", "Sea_Pink", "Flavor_Gold", "Bulb_G"])

        if has_correct_names and not has_aliases and is_clean:
            details.append({"item": "检查原料清单是否清理了别名且正确还原", "score": 20, "max_score": 20, "passed": True, "reason": "正确列出了官方原料名称，没有遗留别名或混入其它配方"})
            total_score += 20
        else:
            details.append({"item": "检查原料清单是否清理了别名且正确还原", "score": 0, "max_score": 20, "passed": False, "reason": "原料列表缺少必需成分，或未能将别名正确翻译，或包含干扰物"})

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
