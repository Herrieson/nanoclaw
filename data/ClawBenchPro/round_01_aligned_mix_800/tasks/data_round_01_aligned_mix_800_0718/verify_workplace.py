import os
import sys
import json
import csv
import re
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables", "best_recipe.json")
    
    score = 0
    details = []

    # 1. 检查目录与文件物理存在性 (10分)
    if os.path.exists(deliverables_path):
        score += 10
        details.append({"item": "文件生成", "score": 10, "max_score": 10, "passed": True, "reason": "成功在 deliverables/ 目录下生成 best_recipe.json"})
    else:
        details.append({"item": "文件生成", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables/best_recipe.json"})
        # 如果文件不存在，后续逻辑无法执行，直接写入结果
        write_result(score, details)
        return

    # 2. 检查 JSON 格式合法性 (10分)
    recipe_data = {}
    try:
        with open(deliverables_path, "r", encoding="utf-8") as f:
            recipe_data = json.load(f)
        score += 10
        details.append({"item": "JSON 格式", "score": 10, "max_score": 10, "passed": True, "reason": "文件内容为合法的 JSON 格式"})
    except Exception as e:
        details.append({"item": "JSON 格式", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        write_result(score, details)
        return

    # 3. 检查字段完整性 (10分)
    required_keys = ["name", "score", "ingredients"]
    missing_keys = [k for k in required_keys if k not in recipe_data]
    if not missing_keys:
        score += 10
        details.append({"item": "字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有必要字段 (name, score, ingredients)"})
    else:
        details.append({"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段: {missing_keys}"})

    # 4. 核心逻辑校验：业务筛选正确性 (70分)
    # 根据题意分析：
    # Recipe A: pH 5.4 (OK), Natural (OK), Score 9.2
    # Recipe B: pH 6.8 (FAIL), Natural (OK), Score 8.5
    # Recipe C: pH 5.5 (OK), Synthetic (FAIL - Dimethicone), Score 9.6
    # Recipe D: pH 5.2 (OK), Natural (OK), Score 9.4
    # 唯一符合条件且最高分的是 Recipe D (Aloe Soothe, Score 9.4)
    
    correct_name = "Aloe Soothe"
    correct_score = 9.4
    correct_ingredients = ["Aloe Vera", "Shea Butter", "Beeswax"]

    # 4.1 校验选择的配方是否正确 (40分)
    if recipe_data.get("name") == correct_name:
        score += 40
        details.append({"item": "配方筛选正确性", "score": 40, "max_score": 40, "passed": True, "reason": "正确筛选出符合条件的最高分配方 Aloe Soothe"})
    else:
        actual_name = recipe_data.get("name")
        reason = f"筛选错误。正确应为 Aloe Soothe，实际为 {actual_name}。"
        if actual_name == "Rose Smooth":
            reason += " (错误原因：未识别出 Dimethicone 为合成成分)"
        elif actual_name == "Lavender Dream":
            reason += " (错误原因：未找到最高分 9.4 的配方)"
        details.append({"item": "配方筛选正确性", "score": 0, "max_score": 40, "passed": False, "reason": reason})

    # 4.2 校验数值提取准确性 (15分)
    try:
        if float(recipe_data.get("score", 0)) == correct_score:
            score += 15
            details.append({"item": "数据提取准确性", "score": 15, "max_score": 15, "passed": True, "reason": "Score 提取准确"})
        else:
            details.append({"item": "数据提取准确性", "score": 0, "max_score": 15, "passed": False, "reason": f"Score 提取不准确，应为 {correct_score}"})
    except:
        details.append({"item": "数据提取准确性", "score": 0, "max_score": 15, "passed": False, "reason": "Score 无法转换为浮点数"})

    # 4.3 校验配料列表准确性 (15分)
    input_ingredients = recipe_data.get("ingredients", [])
    if isinstance(input_ingredients, list) and set([i.strip().lower() for i in input_ingredients]) == set([i.lower() for i in correct_ingredients]):
        score += 15
        details.append({"item": "配料提取准确性", "score": 15, "max_score": 15, "passed": True, "reason": "配料列表提取完整且准确"})
    else:
        details.append({"item": "配料提取准确性", "score": 0, "max_score": 15, "passed": False, "reason": f"配料列表不匹配。应包含: {correct_ingredients}"})

    write_result(score, details)

def write_result(score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": int(score), "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
