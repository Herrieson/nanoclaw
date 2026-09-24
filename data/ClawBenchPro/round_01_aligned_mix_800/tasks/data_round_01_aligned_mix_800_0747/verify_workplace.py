import os
import sys
import json
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    grocery_dir = os.path.join(workspace, "grocery")
    list_file = os.path.join(grocery_dir, "list.json")
    
    # 1. 检查目录和文件是否存在 (10分)
    if os.path.exists(grocery_dir) and os.path.isdir(grocery_dir):
        if os.path.exists(list_file) and os.path.isfile(list_file):
            score_details.append({"item": "检查目标目录和文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "grocery/list.json 存在"})
            total_score += 10
        else:
            score_details.append({"item": "检查目标目录和文件是否存在", "score": 5, "max_score": 10, "passed": False, "reason": "grocery 目录存在，但 list.json 文件缺失"})
    else:
        score_details.append({"item": "检查目标目录和文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "grocery 目录不存在"})

    if total_score < 5:
        write_score(total_score, score_details, workspace)
        return

    # 2. 检查 JSON 格式合法性 (10分)
    try:
        with open(list_file, "r") as f:
            data = json.load(f)
        score_details.append({"item": "检查 JSON 文件格式", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式合法"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "检查 JSON 文件格式", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        write_score(total_score, score_details, workspace)
        return

    # 将所有 key 转小写方便比较
    if not isinstance(data, dict):
        score_details.append({"item": "验证 JSON 数据结构", "score": 0, "max_score": 80, "passed": False, "reason": "JSON 的根节点不是字典/对象结构"})
        write_score(total_score, score_details, workspace)
        return
        
    actual_data = {str(k).strip().lower(): float(v) for k, v in data.items() if str(v).replace('.', '', 1).isdigit()}

    # 3. 检查是否正确排除了违禁品和无效菜谱 (30分)
    forbidden_keys = ['saffron', 'caviar', 'truffle', 'truffles', 'eggs', 'chocolate', 'cream']
    found_forbidden = [k for k in forbidden_keys if k in actual_data]
    if found_forbidden:
        score_details.append({"item": "检查是否剔除昂贵/无效菜谱", "score": 0, "max_score": 30, "passed": False, "reason": f"未正确剔除无效菜谱，发现了被禁止的原料或被抛弃的配方原料: {found_forbidden}"})
    else:
        score_details.append({"item": "检查是否剔除昂贵/无效菜谱", "score": 30, "max_score": 30, "passed": True, "reason": "正确剔除了包含昂贵配料及缺失原料的菜谱"})
        total_score += 30

    # 4. 检查原料提取、求和以及 3 倍批次的计算结果 (50分)
    # Expected: Apples=9, Flour=9, Sugar=4.5, Butter=6, Vanilla=3
    expected_data = {
        "apples": 9.0,
        "flour": 9.0,
        "sugar": 4.5,
        "butter": 6.0,
        "vanilla": 3.0
    }
    
    correct_count = 0
    wrong_items = []
    for k, v in expected_data.items():
        if k in actual_data and abs(actual_data[k] - v) < 0.01:
            correct_count += 1
        else:
            wrong_items.append(f"{k} (预期 {v}, 实际 {actual_data.get(k, '缺失')})")
            
    calc_score = correct_count * 10
    if calc_score == 50:
        score_details.append({"item": "检查最终采购清单及数量计算", "score": 50, "max_score": 50, "passed": True, "reason": "所有合法原料正确汇总并完成了 3 批次的乘法运算"})
    else:
        score_details.append({"item": "检查最终采购清单及数量计算", "score": calc_score, "max_score": 50, "passed": False, "reason": f"计算存在错误: {', '.join(wrong_items)}"})
        
    total_score += calc_score
    
    write_score(total_score, score_details, workspace)

def write_score(total_score, details, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
