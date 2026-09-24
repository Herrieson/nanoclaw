import os
import sys
import json
import csv
import glob

def calculate_ground_truth(workspace):
    # 模拟题目中的生成逻辑，计算唯一正确答案
    # 1. 加载 Sensor Mapping
    mapping_path = os.path.join(workspace, "infrastructure/sensor_mapping.json")
    if not os.path.exists(mapping_path):
        return None
    with open(mapping_path, 'r') as f:
        sensor_map = json.load(f)

    valid_sectors = {"A", "B", "C"}
    results = {}

    # 2. 遍历 telemetry_dumps
    base_dir = os.path.join(workspace, "telemetry_dumps")
    if not os.path.exists(base_dir):
        return None

    for root, dirs, files in os.walk(base_dir):
        # 排除 calibration 文件夹
        if "calibration" in root:
            continue
        
        for file in files:
            # 排除 .log 文件
            if file.endswith(".log"):
                continue
            
            file_path = os.path.join(root, file)
            records = []
            
            try:
                if file.endswith(".json"):
                    with open(file_path, 'r') as f:
                        records = json.load(f)
                elif file.endswith(".csv"):
                    with open(file_path, 'r', newline='') as f:
                        reader = csv.DictReader(f)
                        records = list(reader)
                elif file.endswith(".tsv"):
                    with open(file_path, 'r', newline='') as f:
                        reader = csv.DictReader(f, delimiter='\t')
                        records = list(reader)
                else:
                    continue
            except:
                continue

            for rec in records:
                try:
                    s_id = rec['sensor_id']
                    crop = rec['crop']
                    moisture = float(rec['moisture'])
                    nitrogen = float(rec['nitrogen'])
                    y_val = int(rec['yield'])

                    # 逻辑过滤
                    # Rule: Only Sectors A, B, C
                    if sensor_map.get(s_id) not in valid_sectors:
                        continue
                    # Rule: Nitrogen strictly under 15
                    if nitrogen >= 15:
                        continue
                    # Rule: Moisture between 0 and 100 inclusive
                    if not (0 <= moisture <= 100):
                        continue
                    
                    results[crop] = results.get(crop, 0) + y_val
                except (KeyError, ValueError):
                    continue
    return results

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = "workplace_score.json"
    details = []
    total_score = 0

    # 1. 基础结构检查 (10分)
    cert_dir = os.path.join(workspace, "certification")
    target_file = os.path.join(cert_dir, "certified_yields.json")
    
    dir_exists = os.path.isdir(cert_dir)
    file_exists = os.path.exists(target_file)
    
    if dir_exists and file_exists:
        item_score = 10
        details.append({"item": "目录与文件结构", "score": 10, "max_score": 10, "passed": True, "reason": "certification 目录和 certified_yields.json 均存在"})
    else:
        item_score = 0
        details.append({"item": "目录与文件结构", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失: dir={dir_exists}, file={file_exists}"})
    total_score += item_score

    # 2. 内容合法性解析 (10分)
    agent_data = {}
    if file_exists:
        try:
            with open(target_file, 'r') as f:
                agent_data = json.load(f)
            if isinstance(agent_data, dict) and all(isinstance(v, (int, float)) for v in agent_data.values()):
                details.append({"item": "JSON格式及数据类型", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功且数值均为数字"})
                total_score += 10
            else:
                details.append({"item": "JSON格式及数据类型", "score": 0, "max_score": 10, "passed": False, "reason": "JSON内容结构不符合预期(应为 dict[str, int])"})
        except Exception as e:
            details.append({"item": "JSON格式及数据类型", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
    else:
        details.append({"item": "JSON格式及数据类型", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在，无法解析"})

    # 3. 数据准确性核心检查 (80分)
    ground_truth = calculate_ground_truth(workspace)
    if ground_truth and agent_data:
        # 定义检查项
        crops = ["Corn", "Soy", "Wheat", "Barley", "Tomatoes"]
        correct_count = 0
        for crop in crops:
            expected = ground_truth.get(crop, 0)
            actual = agent_data.get(crop, -1)
            if expected == actual:
                correct_count += 1
        
        # 梯度计分：5个品种，每个16分
        crop_score = correct_count * 16
        total_score += crop_score
        details.append({
            "item": "作物产量数值匹配度",
            "score": crop_score,
            "max_score": 80,
            "passed": correct_count == 5,
            "reason": f"匹配成功 {correct_count}/5 个品种。若为0，请检查是否错误包含了 calibration 目录、D/E 区块或未过滤 Nitrogen/Moisture。"
        })
        
        # 额外惩罚：如果 Agent 输出了多余的字段（例如包含了 Sector D/E 的汇总），酌情扣分
        extra_fields = set(agent_data.keys()) - set(crops)
        if extra_fields:
            penalty = min(total_score, 20)
            total_score -= penalty
            details.append({"item": "多余数据惩罚", "score": -penalty, "max_score": 0, "passed": False, "reason": f"发现了非预期的键: {extra_fields}"})
            
    else:
        details.append({"item": "数值验证", "score": 0, "max_score": 80, "passed": False, "reason": "由于文件缺失或环境破坏，无法进行数值比对"})

    # 写入结果
    with open(score_file, 'w') as f:
        json.dump({"total_score": max(0, total_score), "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
