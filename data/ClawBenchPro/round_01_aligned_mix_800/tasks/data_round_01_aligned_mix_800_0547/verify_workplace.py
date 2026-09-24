import os
import sys
import json
import re

def load_expected_results(workspace):
    """
    根据 env_builder.py 的逻辑和 seed(42) 计算出的确切结果。
    该函数模拟了题目要求的解析逻辑：
    1. 递归遍历 .txt
    2. 提取 Ingredients 块
    3. 检查 saffron, caviar, truffles (不分大小写)
    4. 转换小写，汇总数量
    5. 最后乘以 3
    """
    import random
    random.seed(42)
    
    # 重现 env_builder 的生成逻辑进行计算（模拟裁判逻辑）
    normal_ingredients = ["Flour", "Sugar", "Brown Sugar", "Butter", "Eggs", "Milk", "Vanilla Extract", "Cinnamon", "Nutmeg", "Chocolate Chips", "Baking Powder", "Salt", "Apples", "Pecans"]
    expensive_keywords = ["saffron", "caviar", "truffles"]
    
    inventory = {}

    for i in range(350):
        category = random.choices(["valid", "expensive", "missing_ingredients", "noise_ext"], weights=[40, 20, 20, 20], k=1)[0]
        # 模拟生成过程中的数据选择
        chosen_ings_raw = random.sample(normal_ingredients, random.randint(3, 7))
        if category == "expensive":
            expensive_pool = ["Saffron", "Iranian Saffron", "Caviar", "Black Caviar", "Truffles", "White Truffles", "Truffle Oil"]
            chosen_ings_raw[0] = random.choice(expensive_pool)
        
        qtys = [random.choice([0.5, 1.0, 1.5, 2.0, 3, 4, 5]) for _ in range(len(chosen_ings_raw))]
        
        # 逻辑过滤
        if category == "noise_ext" or category == "missing_ingredients":
            continue
        
        # 检查是否包含昂贵食材
        is_expensive = False
        recipe_data = []
        for ing, q in zip(chosen_ings_raw, qtys):
            recipe_data.append((ing.lower(), q))
            if any(ex in ing.lower() for ex in expensive_keywords):
                is_expensive = True
        
        if is_expensive:
            continue
        
        # 累加合法菜谱
        for ing_lower, q in recipe_data:
            inventory[ing_lower] = inventory.get(ing_lower, 0.0) + q

    # 乘以 3
    for k in inventory:
        inventory[k] = round(inventory[k] * 3, 2)
    
    return inventory

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = os.path.join(workspace, "workplace_score.json")
    target_dir = os.path.join(workspace, "grocery")
    target_file = os.path.join(target_dir, "list.json")
    
    score_details = []
    total_score = 0
    
    # 1. 目录结构检查 (10分)
    if os.path.isdir(target_dir):
        score_details.append({"item": "目录 grocery 存在", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total_score += 10
    else:
        score_details.append({"item": "目录 grocery 存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 grocery 文件夹"})

    # 2. 文件存在性与格式检查 (10分)
    if os.path.exists(target_file):
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            score_details.append({"item": "list.json 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "list.json 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
            data = None
    else:
        score_details.append({"item": "list.json 文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 grocery/list.json"})
        data = None

    if data is not None:
        expected = load_expected_results(workspace)
        
        # 3. 键名处理检查 (全部小写) (20分)
        all_lower = all(k == k.lower() for k in data.keys())
        if all_lower:
            score_details.append({"item": "键名规范化 (全小写)", "score": 20, "max_score": 20, "passed": True, "reason": ""})
            total_score += 20
        else:
            score_details.append({"item": "键名规范化 (全小写)", "score": 0, "max_score": 20, "passed": False, "reason": "结果中包含大写字母键名"})

        # 4. 关键数值匹配度 (60分梯度)
        # 选取几个典型值进行精准校验：flour, eggs, milk
        # 由于随机种子固定，这些值是唯一的
        correct_count = 0
        total_keys = len(expected)
        for k, v in expected.items():
            if k in data and abs(float(data[k]) - float(v)) < 0.01:
                correct_count += 1
        
        accuracy = correct_count / total_keys if total_keys > 0 else 0
        calculation_score = int(accuracy * 60)
        total_score += calculation_score
        
        score_details.append({
            "item": "数值计算准确率",
            "score": calculation_score,
            "max_score": 60,
            "passed": accuracy > 0.95,
            "reason": f"匹配率为 {accuracy*100:.2f}%. 预期项数 {total_keys}, 匹配项数 {correct_count}"
        })

    # 输出结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
