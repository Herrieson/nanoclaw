import os
import sys
import json

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "market_plan.json")
    
    total_score = 0
    details = []

    # Check 1: File existence
    if os.path.exists(report_path):
        total_score += 10
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 reports/market_plan.json 存在"})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "找不到文件 reports/market_plan.json"})
        # File doesn't exist, we can't test further
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # Check 2: JSON Parsing
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        total_score += 10
        details.append({"item": "检查文件是否为合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
    except Exception as e:
        details.append({"item": "检查文件是否为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # Check 3: Total Cost
    data_str = json.dumps(data).lower()
    # Need to extract total cost robustly since schema is not strictly defined, 
    # but we can look for the number 340.0
    # Expected total is 120.0 + 150.0 + 70.0 = 340.0
    # Search recursively for numeric values or string numeric values
    def extract_numbers(obj):
        nums = []
        if isinstance(obj, dict):
            for v in obj.values():
                nums.extend(extract_numbers(v))
        elif isinstance(obj, list):
            for v in obj:
                nums.extend(extract_numbers(v))
        elif isinstance(obj, (int, float)):
            nums.append(float(obj))
        elif isinstance(obj, str):
            try:
                nums.append(float(obj))
            except ValueError:
                pass
        return nums
    
    numbers_found = extract_numbers(data)
    if 340.0 in numbers_found or 340 in numbers_found:
        total_score += 30
        details.append({"item": "检查总价值计算是否正确", "score": 30, "max_score": 30, "passed": True, "reason": "找到了正确的总金额 340"})
    else:
        details.append({"item": "检查总价值计算是否正确", "score": 0, "max_score": 30, "passed": False, "reason": f"未找到正确总金额 340.0, 找到的数字有: {numbers_found}"})

    # Check 4: Included Items
    expected_items = ["local honey", "free-range eggs", "sustainable oats"]
    included_score = 0
    passed_items = []
    for item in expected_items:
        if item in data_str:
            included_score += 10
            passed_items.append(item)
    
    total_score += included_score
    details.append({
        "item": "检查清单是否包含必须的合格商品",
        "score": included_score,
        "max_score": 30,
        "passed": included_score == 30,
        "reason": f"包含的必须商品: {passed_items}"
    })

    # Check 5: Exclusion of invalid items
    invalid_items = ["organic apples", "organic kale", "organic berries", "plastic bottled soda", "industrial white sugar"]
    found_invalid = []
    for item in invalid_items:
        if item in data_str:
            found_invalid.append(item)
    
    if len(found_invalid) == 0:
        total_score += 20
        details.append({"item": "检查是否排除了过期商品和工业品", "score": 20, "max_score": 20, "passed": True, "reason": "完美排除了所有违规/过期商品"})
    else:
        penalty = min(20, len(found_invalid) * 10)
        score = 20 - penalty
        total_score += score
        details.append({"item": "检查是否排除了过期商品和工业品", "score": score, "max_score": 20, "passed": False, "reason": f"未正确排除以下商品: {found_invalid}"})

    # Output final results
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify_workplace()
