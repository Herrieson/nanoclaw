import os
import sys
import json
import math

def verify_workplace(workspace):
    score_details = []
    total_score = 0
    
    file_path = os.path.join(workspace, "hike_manifest.json")
    
    # 1. Check if file exists (20 pts)
    if os.path.exists(file_path):
        score_details.append({"item": "检查 hike_manifest.json 是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件已生成"})
        total_score += 20
    else:
        score_details.append({"item": "检查 hike_manifest.json 是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件未找到"})
        return {"total_score": total_score, "details": score_details}
        
    # 2. Check JSON validity and schema (20 pts)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if not isinstance(data, dict):
            raise ValueError("Root must be a JSON object")
            
        has_trail = "trail_name" in data
        has_weight = "needed_gear_weight_kg" in data
        
        if has_trail and has_weight:
            # Check for hallucinations / extra fields
            if len(data.keys()) > 3: # Allow maybe 1 extra harmless key, but penalize if heavily bloated
                score_details.append({"item": "检查 JSON Schema", "score": 10, "max_score": 20, "passed": False, "reason": "包含了要求的字段，但存在多余的幻觉字段或不合规键值"})
                total_score += 10
            else:
                score_details.append({"item": "检查 JSON Schema", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 结构合法且字段严格对应"})
                total_score += 20
        else:
            score_details.append({"item": "检查 JSON Schema", "score": 0, "max_score": 20, "passed": False, "reason": "缺少必要的 trail_name 或 needed_gear_weight_kg 字段"})
            
    except Exception as e:
        score_details.append({"item": "检查 JSON Schema", "score": 0, "max_score": 20, "passed": False, "reason": f"解析失败: {str(e)}"})
        return {"total_score": total_score, "details": score_details}

    # 3. Check Trail Name (30 pts)
    # The only correct trail is "Little Bear Loop"
    target_trail = "Little Bear Loop"
    actual_trail = str(data.get("trail_name", "")).strip()
    if actual_trail == target_trail:
        score_details.append({"item": "检查选定步道是否正确", "score": 30, "max_score": 30, "passed": True, "reason": f"成功识别唯一正确的步道: {actual_trail}"})
        total_score += 30
    else:
        score_details.append({"item": "检查选定步道是否正确", "score": 0, "max_score": 30, "passed": False, "reason": f"选定步道错误或未满足所有过滤条件: {actual_trail}"})

    # 4. Check Gear Weight Calculation (30 pts)
    # Expected total weight:
    # Sleeping Bag Adult 1: 45.0 oz -> 1.2757275
    # Toddler Sleeping Bag: 25.5 oz -> 0.72291225
    # Water Filter: 340.0 g -> 0.34
    # Camp Stove: 1.5 lbs -> 24.0 oz -> 0.680388
    # First Aid Kit: 22.0 oz -> 0.623689
    # Total -> 3.64271675 kg
    target_weight = 3.64271675
    
    try:
        actual_weight = float(data.get("needed_gear_weight_kg", 0))
        # Allow small floating point tolerance (e.g., due to rounding or slight calculation variations)
        if math.isclose(actual_weight, target_weight, abs_tol=0.01):
            score_details.append({"item": "检查装备重量计算是否准确", "score": 30, "max_score": 30, "passed": True, "reason": f"计算精度符合要求: {actual_weight} kg"})
            total_score += 30
        else:
            score_details.append({"item": "检查装备重量计算是否准确", "score": 0, "max_score": 30, "passed": False, "reason": f"重量计算错误，期望 {target_weight:.4f} 左右，实际 {actual_weight}"})
    except (ValueError, TypeError):
        score_details.append({"item": "检查装备重量计算是否准确", "score": 0, "max_score": 30, "passed": False, "reason": "重量数值格式非法，无法转换为浮点数"})

    return {"total_score": total_score, "details": score_details}

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify_workplace(workspace_dir)
    
    with open(os.path.join(workspace_dir, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
