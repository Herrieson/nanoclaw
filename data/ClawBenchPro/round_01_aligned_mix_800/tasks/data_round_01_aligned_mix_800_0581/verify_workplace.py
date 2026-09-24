import os
import sys
import json
import csv
import glob
import math

def calculate_expected_results(workspace):
    """
    独立于 Agent 逻辑，通过标准算法计算正确答案
    """
    # 1. Load Reference Guide
    ref_path = os.path.join(workspace, "reference_guide", "materials.json")
    with open(ref_path, 'r') as f:
        material_map = json.load(f)

    # 2. Load Safety Clearance
    approved_batches = set()
    clearance_path = os.path.join(workspace, "safety_clearance", "clearance_db.csv")
    with open(clearance_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['status'] == 'APPROVED':
                approved_batches.add(row['batch_id'])

    # 3. Process Inventory Logs
    totals = {"Wood": 0.0, "Fabric": 0.0, "Glass": 0.0}
    toxic_keywords = ["styrofoam", "pvc", "lead"]
    target_cats = ["wood", "fabric", "glass"]

    # Traverse all files
    log_files = glob.glob(os.path.join(workspace, "inventory_logs", "**", "*.*"), recursive=True)
    
    for file_path in log_files:
        items = []
        batch_id = None
        
        if file_path.endswith(".json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    batch_id = data.get("batch_reference")
                    items = data.get("items", [])
            except: continue
        elif file_path.endswith(".csv"):
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    # Find batch_id in header
                    for line in lines:
                        if line.startswith("batch_id"):
                            batch_id = line.split(",")[1].strip()
                            break
                    # Parse data lines
                    data_start = 0
                    for i, line in enumerate(lines):
                        if "material_code" in line:
                            data_start = i
                            break
                    reader = csv.DictReader(lines[data_start:])
                    for row in reader:
                        items.append({
                            "code": row["material_code"],
                            "qty": float(row["quantity"]),
                            "unit": row["weight_unit"]
                        })
            except: continue
        
        # Filter by approval
        if batch_id not in approved_batches:
            continue
            
        for item in items:
            m_code = item["code"]
            if m_code not in material_map: continue
            
            desc = material_map[m_code].lower()
            
            # Toxic check
            if any(tk in desc for tk in toxic_keywords):
                continue
            
            # Category check
            cat_found = None
            for tc in target_cats:
                if tc in desc:
                    cat_found = tc.capitalize()
                    break
            
            if not cat_found: continue
            
            # Conversion
            qty = float(item["qty"])
            unit = item["unit"].lower()
            if unit == "lbs":
                qty *= 0.453592
            elif unit == "oz":
                qty *= 0.0283495
            # Already in kg or other? Prompt says only kg/lbs/oz
            
            totals[cat_found] += qty

    return {k: round(v, 2) for k, v in totals.items()}

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. Directory Structure (10 points)
    output_dir = os.path.join(workspace, "craft_plans")
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        score += 10
        details.append({"item": "目录结构", "score": 10, "max_score": 10, "passed": True, "reason": "craft_plans 目录已创建"})
    else:
        details.append({"item": "目录结构", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 craft_plans 目录"})

    # 2. File Presence & Format (20 points)
    output_file = os.path.join(output_dir, "clean_inventory.json")
    if not os.path.exists(output_file):
        details.append({"item": "输出文件", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 clean_inventory.json"})
    else:
        try:
            with open(output_file, 'r') as f:
                output_data = json.load(f)
            score += 20
            details.append({"item": "输出文件", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 格式解析成功"})
            
            # 3. Content Accuracy (70 points)
            expected = calculate_expected_results(workspace)
            correct_count = 0
            for key in ["Wood", "Fabric", "Glass"]:
                agent_val = output_data.get(key)
                exp_val = expected.get(key)
                # Allow minor float precision diff but round(2) should be exact
                if agent_val == exp_val:
                    correct_count += 1
                else:
                    details.append({"item": f"数值校验: {key}", "score": 0, "max_score": 23, "passed": False, "reason": f"期望 {exp_val}, 得到 {agent_val}"})
            
            # Allocation: 23+23+24 = 70
            points_per_key = [23, 23, 24]
            current_points = sum(points_per_key[:correct_count])
            score += current_points
            if correct_count == 3:
                 details.append({"item": "数值准确性", "score": 70, "max_score": 70, "passed": True, "reason": "三个类别的总重完全匹配"})
            
        except Exception as e:
            details.append({"item": "JSON 解析", "score": 0, "max_score": 20, "passed": False, "reason": f"文件内容错误: {str(e)}"})

    # Final Output
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
