import os
import sys
import json
import csv
import re
import math

def calculate_expected(workspace):
    """
    基于环境动态计算 Ground Truth，确保极强的鲁棒性
    """
    codes_path = os.path.join(workspace, "compliance", "certification_codes.json")
    inspectors_path = os.path.join(workspace, "compliance", "inspector_registry.csv")
    logs_dir = os.path.join(workspace, "archives", "dock_logs")
    
    if not os.path.exists(codes_path) or not os.path.exists(inspectors_path) or not os.path.exists(logs_dir):
        return None
        
    # 1. 还原有机代号
    with open(codes_path, "r", encoding="utf-8") as f:
        codes = json.load(f)
    organic_codes = {k for k, v in codes.items() if v == "Certified Organic"}
    
    # 2. 还原 Active 检查员名单
    active_inspectors = set()
    with open(inspectors_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Status"] == "Active":
                active_inspectors.add(row["Inspector_ID"])
                
    totals = {}
    
    def process_item(item_data):
        ing = item_data.get("item")
        cert = item_data.get("cert_code")
        ins = item_data.get("inspector")
        weight_str = str(item_data.get("weight", "")).strip().lower()
        
        if ins in active_inspectors and cert in organic_codes:
            # 解析数字和单位
            match = re.match(r"^([\d\.]+)\s*(kg|oz|lbs|)$", weight_str)
            if not match:
                return
            val = float(match.group(1))
            unit = match.group(2)
            
            # 单位换算
            if unit == "kg":
                val *= 2.2
            elif unit == "oz":
                val *= 0.0625
                
            totals[ing] = totals.get(ing, 0) + val

    # 3. 递归遍历日志文件
    for root, _, files in os.walk(logs_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            if file.endswith(".json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for item in data.get("payload", {}).get("items", []):
                            process_item(item)
                except Exception:
                    pass
                    
            elif file.endswith(".csv") and "inspector_registry" not in file:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            process_item({
                                "item": row.get("ItemName"),
                                "cert_code": row.get("Code"),
                                "inspector": row.get("Inspector"),
                                "weight": row.get("Weight_Value")
                            })
                except Exception:
                    pass
                    
            elif file.endswith(".txt"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if "Bat Mitzvah" in content:
                            continue # 忽略女儿派对垃圾数据
                        for line in content.split("\n"):
                            match = re.search(r"\[(.*?)\] Received (.*?) - Weight: (.*?) \(Status: (.*?)\)", line)
                            if match:
                                process_item({
                                    "inspector": match.group(1),
                                    "item": match.group(2),
                                    "weight": match.group(3),
                                    "cert_code": match.group(4)
                                })
                except Exception:
                    pass
                    
    return {k: round(v, 2) for k, v in totals.items()}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "inventory_reports", "certified_totals.json")
    
    score_details = []
    total_score = 0
    
    # 验证项 1: 文件是否存在 (10分)
    file_exists = os.path.exists(target_file)
    if file_exists:
        score_details.append({"item": "检查目标文件 certified_totals.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已成功生成"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标文件 certified_totals.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
    
    # 验证项 2: JSON 格式校验 (10分)
    agent_data = {}
    is_valid_json = False
    if file_exists:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                agent_data = json.load(f)
            if isinstance(agent_data, dict):
                is_valid_json = True
                score_details.append({"item": "检查 JSON 格式与顶层数据结构", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功，并且是字典结构"})
                total_score += 10
            else:
                score_details.append({"item": "检查 JSON 格式与顶层数据结构", "score": 0, "max_score": 10, "passed": False, "reason": "JSON顶层结构应为字典"})
        except Exception as e:
            score_details.append({"item": "检查 JSON 格式与顶层数据结构", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
            
    # 计算 Ground Truth
    expected_data = calculate_expected(workspace)
    if expected_data is None:
        expected_data = {} # 避免系统错误导致全盘崩溃

    # 验证项 3: 键（成分名）的完整性与无幻觉 (20分)
    if is_valid_json and expected_data:
        expected_keys = set(expected_data.keys())
        agent_keys = set(agent_data.keys())
        
        missing_keys = expected_keys - agent_keys
        extra_keys = agent_keys - expected_keys
        
        if not missing_keys and not extra_keys:
            score_details.append({"item": "检查成分名称是否齐全且无多余项", "score": 20, "max_score": 20, "passed": True, "reason": "成分列表完美匹配预期"})
            total_score += 20
        else:
            reason_str = ""
            if missing_keys: reason_str += f"缺失: {missing_keys}。 "
            if extra_keys: reason_str += f"多余(幻觉/错误过滤): {extra_keys}。 "
            
            # 部分给分逻辑：如果只缺失一部分，给10分；如果出现多余成分（严重过滤失败），给0分。
            if extra_keys:
                score_details.append({"item": "检查成分名称是否齐全且无多余项", "score": 0, "max_score": 20, "passed": False, "reason": "过滤失败！包含了无效或无用的成分。"})
            else:
                score_details.append({"item": "检查成分名称是否齐全且无多余项", "score": 10, "max_score": 20, "passed": False, "reason": f"部分成分缺失: {reason_str}"})
                total_score += 10

    # 验证项 4: 数值计算精确度校验 (60分)
    if is_valid_json and expected_data:
        points_per_item = 60 / len(expected_data)
        calc_score = 0
        error_items = []
        
        for key, expected_val in expected_data.items():
            if key in agent_data:
                try:
                    agent_val = float(agent_data[key])
                    # 容许 0.1 lbs 的浮点数误差
                    if math.isclose(agent_val, expected_val, abs_tol=0.1):
                        calc_score += points_per_item
                    else:
                        error_items.append(f"{key} (预期:{expected_val}, 实际:{agent_val})")
                except ValueError:
                    error_items.append(f"{key} 值类型错误")
            else:
                error_items.append(f"{key} 缺失")
                
        calc_score = round(calc_score)
        total_score += calc_score
        
        if not error_items:
            score_details.append({"item": "核对最终重量计算结果", "score": 60, "max_score": 60, "passed": True, "reason": "所有有机成分的总重量计算完全准确！"})
        else:
            score_details.append({"item": "核对最终重量计算结果", "score": calc_score, "max_score": 60, "passed": False, "reason": f"部分数值计算错误: {', '.join(error_items)}"})

    # 写入验证结果
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
