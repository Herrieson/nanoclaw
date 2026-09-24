import os
import sys
import json
import csv
import glob
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # ---------------------------------------------------------
    # 1. Server-side Truth Calculation (Code Probe)
    # ---------------------------------------------------------
    
    # 1.1 Read Valid Volunteers from JSONs
    valid_vids = {}
    registry_path = os.path.join(workspace, "registry", "zone_*", "*.json")
    for filepath in glob.glob(registry_path):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for rec in data.get("records", []):
                    # Condition: active AND born in 2008 or earlier
                    if rec.get("status") == "active" and rec.get("dob", 9999) <= 2008:
                        valid_vids[rec["vid"]] = rec["name"]
        except Exception:
            pass

    # 1.2 Identify Eco-Friendly Equipment Codes
    reusable_codes = set()
    equipment_path = os.path.join(workspace, "assets", "equipment.yaml")
    if os.path.exists(equipment_path):
        try:
            import yaml
            with open(equipment_path, "r", encoding="utf-8") as f:
                eq_data = yaml.safe_load(f)
                for item in eq_data.get("categories", {}).get("hydration_gear", []):
                    if item.get("eco_friendly") is True:
                        reusable_codes.add(item["code"])
        except Exception:
            # Fallback based on env_builder
            reusable_codes = {"HYD-REUSE-01", "HYD-REUSE-02", "HYD-REUSE-03"}
    else:
        reusable_codes = {"HYD-REUSE-01", "HYD-REUSE-02", "HYD-REUSE-03"}

    # 1.3 Scan Checkpoint Logs for Eco-Friendly Gear
    eco_vids = set()
    checkpoints_path = os.path.join(workspace, "checkpoints", "*.log")
    for filepath in glob.glob(checkpoints_path):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if "|" in line and "V-" in line:
                        parts = line.split("|")
                        vid_part = parts[0]
                        items_part = parts[1]
                        
                        vid_match = re.search(r"(V-\d{4})", vid_part)
                        if vid_match:
                            vid = vid_match.group(1)
                            items = [x.strip() for x in items_part.split(",")]
                            if any(item in reusable_codes for item in items):
                                eco_vids.add(vid)
        except Exception:
            pass

    # 1.4 Calculate Intersection of Surving Elites
    final_vids = set(valid_vids.keys()).intersection(eco_vids)
    expected_names = set(valid_vids[v] for v in final_vids)
    
    # 1.5 Calculate Total Hours from Commitments CSV
    expected_hours = 0
    csv_path = os.path.join(workspace, "planning", "commitments.csv")
    if os.path.exists(csv_path):
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    vid = row.get("volunteer_id")
                    if vid in final_vids:
                        shifts = int(row.get("shifts", 0))
                        hps = int(row.get("hours_per_shift", 0))
                        expected_hours += (shifts * hps)
        except Exception:
            pass

    # ---------------------------------------------------------
    # 2. Evaluation Phase
    # ---------------------------------------------------------
    score = 0
    details = []
    
    deliv_dir = os.path.join(workspace, "deliverables")
    json_path = os.path.join(deliv_dir, "ready_volunteers.json")
    agent_data = None

    # Check 1: Directory Existence (10 points)
    if os.path.isdir(deliv_dir):
        score += 10
        details.append({"item": "检查目标目录 deliverables 是否创建", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        details.append({"item": "检查目标目录 deliverables 是否创建", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})

    # Check 2: File Existence and Valid JSON (10 points)
    if os.path.isfile(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                agent_data = json.load(f)
            score += 10
            details.append({"item": "检查 JSON 文件是否存在且格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "文件合法可解析"})
        except Exception as e:
            details.append({"item": "检查 JSON 文件是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
    else:
        details.append({"item": "检查 JSON 文件是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 ready_volunteers.json"})

    # Check 3, 4, 5: Schema and Data Verification
    if agent_data is not None and isinstance(agent_data, dict):
        keys = set(agent_data.keys())
        
        # Check 3: Strict Schema (20 points)
        if keys == {"names", "total_combined_hours"}:
            score += 20
            details.append({"item": "检查 JSON Schema 无冗余字段", "score": 20, "max_score": 20, "passed": True, "reason": "精确包含 names 和 total_combined_hours"})
        else:
            details.append({"item": "检查 JSON Schema 无冗余字段", "score": 0, "max_score": 20, "passed": False, "reason": f"预期只有 ['names', 'total_combined_hours'], 实际给出 {list(keys)}，涉嫌捏造数据或未遵循要求"})

        # Check 4: Names Array Strict Match (30 points)
        agent_names = agent_data.get("names", [])
        if isinstance(agent_names, list):
            agent_names_set = set(agent_names)
            intersect = expected_names.intersection(agent_names_set)
            union = expected_names.union(agent_names_set)
            iou = len(intersect) / len(union) if len(union) > 0 else 0
            
            name_score = int(30 * iou)
            score += name_score
            passed = (name_score == 30)
            details.append({"item": "名单准确度检测 (IoU)", "score": name_score, "max_score": 30, "passed": passed, "reason": f"预期 {len(expected_names)} 人，实际给出 {len(agent_names)} 人。匹配度(IoU): {iou:.2f}"})
        else:
            details.append({"item": "名单准确度检测 (IoU)", "score": 0, "max_score": 30, "passed": False, "reason": "字段 names 不是列表类型"})

        # Check 5: Hours Strict Match (30 points)
        agent_hours = agent_data.get("total_combined_hours")
        if isinstance(agent_hours, (int, float)) and agent_hours == expected_hours:
            score += 30
            details.append({"item": "总时长精准计算", "score": 30, "max_score": 30, "passed": True, "reason": f"精确匹配总时长: {expected_hours}"})
        else:
            details.append({"item": "总时长精准计算", "score": 0, "max_score": 30, "passed": False, "reason": f"计算错误或格式不对。预期: {expected_hours}, 实际: {agent_hours}"})
    else:
        if agent_data is not None:
            details.append({"item": "数据内容验证", "score": 0, "max_score": 80, "passed": False, "reason": "JSON根节点必须是Object(字典)"})

    # Write output score
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
