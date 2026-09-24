import os
import sys
import json
import csv

def compute_ground_truth(workspace):
    registry_path = os.path.join(workspace, "reactor_data", "registry", "master_registry.json")
    if not os.path.exists(registry_path):
        return [], [], 0

    with open(registry_path, "r") as f:
        registry = json.load(f)
    
    valid_reactors = set()
    for r in registry.get("reactors", []):
        if r.get("status") == "ONLINE" and r.get("certification") == "VALID":
            valid_reactors.add(r.get("reactor_id"))
            
    logs_dir = os.path.join(workspace, "reactor_data", "logs")
    critical_failures = set()
    green_failures = set()
    total_waste = 0.0
    
    if not os.path.exists(logs_dir):
        return [], [], 0

    for root, dirs, files in os.walk(logs_dir):
        for file in files:
            if file.endswith(".bak") or file.endswith(".tmp"):
                continue
            
            full_path = os.path.join(root, file)
            try:
                if file.endswith(".csv"):
                    with open(full_path, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            b_id = row["batch_id"]
                            r_id = row["reactor_id"]
                            temp = float(row["temp_c"])
                            weight = float(row["total_weight_kg"])
                            recycled = float(row["recycled_content_kg"])
                            output = float(row["output_product_kg"])
                            
                            if r_id in valid_reactors:
                                if temp > 220.0:
                                    critical_failures.add(b_id)
                                if recycled < 0.15 * weight:
                                    green_failures.add(b_id)
                                total_waste += (weight - output)
                                
                elif file.endswith(".json"):
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for row in data:
                            b_id = row["batch_id"]
                            r_id = row["reactor"]
                            temp = float(row["temperature"])
                            weight = float(row["weight"])
                            recycled = float(row["recycled"])
                            output = float(row["output"])
                            
                            if r_id in valid_reactors:
                                if temp > 220.0:
                                    critical_failures.add(b_id)
                                if recycled < 0.15 * weight:
                                    green_failures.add(b_id)
                                total_waste += (weight - output)
                                
                elif file.endswith(".log"):
                    with open(full_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line or "[BATCH]" not in line: continue
                            parts = line.split(" | ")
                            b_id = parts[0].split("ID:")[1]
                            r_id = parts[1].split("R_ID:")[1]
                            temp = float(parts[2].split("TEMP:")[1])
                            weight = float(parts[3].split("MASS:")[1])
                            recycled = float(parts[4].split("RECYCLED_MASS:")[1])
                            output = float(parts[5].split("YIELD:")[1])
                            
                            if r_id in valid_reactors:
                                if temp > 220.0:
                                    critical_failures.add(b_id)
                                if recycled < 0.15 * weight:
                                    green_failures.add(b_id)
                                total_waste += (weight - output)
            except Exception as e:
                pass
                            
    gt_critical = sorted(list(critical_failures))
    gt_green = sorted(list(green_failures))
    return gt_critical, gt_green, total_waste

def verify(workspace):
    details = []
    total_score = 0
    
    # 1. 检查目标文件是否存在 (10 分)
    result_path = os.path.join(workspace, "audit_results", "summary.json")
    if not os.path.exists(result_path):
        details.append({"item": "检查 summary.json 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 audit_results/summary.json 文件"})
        return 0, details
    
    details.append({"item": "检查 summary.json 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    total_score += 10
    
    # 2. 检查 JSON 格式与键值结构 (15 分)
    try:
        with open(result_path, "r", encoding="utf-8") as f:
            user_data = json.load(f)
    except json.JSONDecodeError:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 解析失败，格式不合法"})
        return total_score, details

    expected_keys = {"critical_failures", "green_failures", "total_waste_kg"}
    actual_keys = set(user_data.keys())
    
    if expected_keys.issubset(actual_keys):
        score_keys = 10
        reason_keys = "包含了所有必须的键"
        if actual_keys == expected_keys:
            score_keys = 15
            reason_keys = "包含了所有必须的键且没有多余捏造字段"
        details.append({"item": "检查 JSON 键值要求", "score": score_keys, "max_score": 15, "passed": True, "reason": reason_keys})
        total_score += score_keys
    else:
        details.append({"item": "检查 JSON 键值要求", "score": 0, "max_score": 15, "passed": False, "reason": f"缺失核心键值: {expected_keys - actual_keys}"})
        return total_score, details
        
    # 计算 Ground Truth
    gt_critical, gt_green, gt_total_waste = compute_ground_truth(workspace)
    
    # 3. 验证 Critical Failures (25 分)
    user_critical = user_data.get("critical_failures", [])
    if not isinstance(user_critical, list):
        details.append({"item": "验证 Critical Failures 结果", "score": 0, "max_score": 25, "passed": False, "reason": "critical_failures 必须是列表"})
    elif sorted(user_critical) == gt_critical:
        details.append({"item": "验证 Critical Failures 结果", "score": 25, "max_score": 25, "passed": True, "reason": "数据过滤与温度阈值计算完全正确"})
        total_score += 25
    else:
        details.append({"item": "验证 Critical Failures 结果", "score": 0, "max_score": 25, "passed": False, "reason": f"结果错误。可能未正确读取有效的 reactor 或未排除脏数据。"})

    # 4. 验证 Green Failures (25 分)
    user_green = user_data.get("green_failures", [])
    if not isinstance(user_green, list):
        details.append({"item": "验证 Green Failures 结果", "score": 0, "max_score": 25, "passed": False, "reason": "green_failures 必须是列表"})
    elif sorted(user_green) == gt_green:
        details.append({"item": "验证 Green Failures 结果", "score": 25, "max_score": 25, "passed": True, "reason": "数据过滤与回收物比例计算完全正确"})
        total_score += 25
    else:
        details.append({"item": "验证 Green Failures 结果", "score": 0, "max_score": 25, "passed": False, "reason": "结果错误。比例计算或多态数据解析可能有误。"})

    # 5. 验证 Total Waste (25 分)
    user_waste = user_data.get("total_waste_kg", None)
    if not isinstance(user_waste, (int, float)):
        details.append({"item": "验证 Total Waste 结果", "score": 0, "max_score": 25, "passed": False, "reason": "total_waste_kg 必须是数字"})
    elif abs(float(user_waste) - gt_total_waste) < 1.0:
        details.append({"item": "验证 Total Waste 结果", "score": 25, "max_score": 25, "passed": True, "reason": "总废料计算完全准确"})
        total_score += 25
    else:
        details.append({"item": "验证 Total Waste 结果", "score": 0, "max_score": 25, "passed": False, "reason": "计算存在偏差，可能读取了备份文件 (.bak/.tmp) 或错误的 registry 数据。"})

    return total_score, details

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    score, details = verify(workspace_dir)
    
    with open(os.path.join(workspace_dir, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": score,
            "details": details
        }, f, indent=4, ensure_ascii=False)
