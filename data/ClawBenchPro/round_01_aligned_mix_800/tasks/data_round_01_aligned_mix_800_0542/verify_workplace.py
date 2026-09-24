import os
import sys
import json
import csv
import glob

def generate_golden_data(workspace):
    # Load approved registry
    registry_path = None
    for f in os.listdir(os.path.join(workspace, "reference")):
        if "approved" in f.lower() and f.endswith(".json"):
            registry_path = os.path.join(workspace, "reference", f)
            break
            
    if not registry_path:
        raise FileNotFoundError("Could not find approved registry for golden data generation.")
        
    with open(registry_path, 'r') as f:
        registry = json.load(f)
        
    quarantine_records = []
    cii_records = []
    tally = {}
    
    # Process logs
    logs_dir = os.path.join(workspace, "logs", "weekend_dumps")
    for root, _, files in os.walk(logs_dir):
        for file in files:
            filepath = os.path.join(root, file)
            if file.endswith('.json'):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    if not isinstance(data, list):
                        continue
                    for rec in data:
                        # Check required fields
                        if not all(k in rec for k in ("code", "batch", "exp", "qty")): continue
                        if not all(str(rec[k]).strip() for k in ("code", "batch", "exp", "qty")): continue
                        
                        code = str(rec["code"]).strip()
                        batch = str(rec["batch"]).strip()
                        exp = str(rec["exp"]).strip()
                        qty = int(rec["qty"])
                        
                        if code not in registry: continue
                        year = int(exp.split('-')[0])
                        name = registry[code]["name"]
                        schedule = registry[code]["schedule"]
                        
                        row = [code, name, batch, exp, str(qty)]
                        if year <= 2023:
                            quarantine_records.append(row)
                        else:
                            if schedule == "CII":
                                cii_records.append(row)
                            else:
                                tally[name] = tally.get(name, 0) + qty
                except Exception:
                    pass
            elif file.endswith('.csv'):
                try:
                    with open(filepath, 'r') as f:
                        reader = csv.DictReader(f)
                        if not reader.fieldnames or not all(k in reader.fieldnames for k in ("code", "batch", "exp", "qty")):
                            continue
                        for row in reader:
                            if not all(k in row for k in ("code", "batch", "exp", "qty")): continue
                            if not all(str(row[k]).strip() for k in ("code", "batch", "exp", "qty")): continue
                            
                            code = str(row["code"]).strip()
                            batch = str(row["batch"]).strip()
                            exp = str(row["exp"]).strip()
                            qty_val = str(row["qty"]).strip()
                            # It's possible qty has non-integer garbage in corrupt files, let's try
                            try:
                                qty = int(qty_val)
                            except ValueError:
                                continue
                                
                            if code not in registry: continue
                            year = int(exp.split('-')[0])
                            name = registry[code]["name"]
                            schedule = registry[code]["schedule"]
                            
                            csv_row = [code, name, batch, exp, str(qty)]
                            if year <= 2023:
                                quarantine_records.append(csv_row)
                            else:
                                if schedule == "CII":
                                    cii_records.append(csv_row)
                                else:
                                    tally[name] = tally.get(name, 0) + qty
                except Exception:
                    pass

    # Sort
    quarantine_records.sort(key=lambda x: (x[0], x[2]))
    cii_records.sort(key=lambda x: (x[0], x[2]))
    
    return quarantine_records, cii_records, tally

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    try:
        golden_quarantine, golden_cii, golden_tally = generate_golden_data(workspace)
    except Exception as e:
        print(f"Failed to generate golden data: {e}")
        sys.exit(1)

    deliverables_dir = os.path.join(workspace, "deliverables")
    
    # Check 1: Directory and File Extraneous (10 pts)
    item_dir = {"item": "检查deliverables目录与文件纯净度", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if os.path.isdir(deliverables_dir):
        files = os.listdir(deliverables_dir)
        expected_files = {"quarantine.csv", "cii_alerts.csv", "valid_tally.json"}
        actual_files = set(files)
        if actual_files == expected_files:
            item_dir["score"] = 10
            item_dir["passed"] = True
            item_dir["reason"] = "目录存在且仅包含预期的三个文件"
        else:
            item_dir["score"] = 5
            item_dir["reason"] = f"目录存在但文件不完全匹配。预期: {expected_files}, 实际: {actual_files}"
    else:
        item_dir["reason"] = "deliverables 目录不存在"
    score_details.append(item_dir)
    total_score += item_dir["score"]

    # Check 2: quarantine.csv (30 pts)
    quarantine_path = os.path.join(deliverables_dir, "quarantine.csv")
    item_q_read = {"item": "quarantine.csv 存在且格式正确", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    item_q_data = {"item": "quarantine.csv 数据完整性与排序", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    
    agent_quarantine = []
    if os.path.exists(quarantine_path):
        try:
            with open(quarantine_path, 'r', encoding='utf-8') as f:
                reader = list(csv.reader(f))
                if len(reader) > 0 and reader[0] == ["code", "name", "batch", "exp", "qty"]:
                    item_q_read["score"] = 10
                    item_q_read["passed"] = True
                    item_q_read["reason"] = "文件可读且包含正确的 Header"
                    agent_quarantine = reader[1:]
                else:
                    item_q_read["score"] = 5
                    item_q_read["reason"] = "文件可读但 Header 不匹配"
                    if len(reader) > 0 and reader[0][0] != 'code':
                        pass # probably headerless
                    elif len(reader) > 0:
                        agent_quarantine = reader[1:]
                        
            if item_q_read["passed"]:
                if agent_quarantine == golden_quarantine:
                    item_q_data["score"] = 20
                    item_q_data["passed"] = True
                    item_q_data["reason"] = "过期数据过滤、关联、排序完全准确无误"
                else:
                    item_q_data["reason"] = f"数据存在错误。预期行数 {len(golden_quarantine)}，实际行数 {len(agent_quarantine)}"
        except Exception as e:
            item_q_read["reason"] = f"读取异常: {e}"
    else:
        item_q_read["reason"] = "文件不存在"
        
    score_details.extend([item_q_read, item_q_data])
    total_score += item_q_read["score"] + item_q_data["score"]

    # Check 3: cii_alerts.csv (30 pts)
    cii_path = os.path.join(deliverables_dir, "cii_alerts.csv")
    item_c_read = {"item": "cii_alerts.csv 存在且格式正确", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    item_c_data = {"item": "cii_alerts.csv 数据完整性与排序", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    
    agent_cii = []
    if os.path.exists(cii_path):
        try:
            with open(cii_path, 'r', encoding='utf-8') as f:
                reader = list(csv.reader(f))
                if len(reader) > 0 and reader[0] == ["code", "name", "batch", "exp", "qty"]:
                    item_c_read["score"] = 10
                    item_c_read["passed"] = True
                    item_c_read["reason"] = "文件可读且包含正确的 Header"
                    agent_cii = reader[1:]
                else:
                    item_c_read["score"] = 5
                    item_c_read["reason"] = "文件可读但 Header 不匹配"
                    if len(reader) > 0 and reader[0][0] == 'code':
                        agent_cii = reader[1:]
                        
            if item_c_read["passed"]:
                if agent_cii == golden_cii:
                    item_c_data["score"] = 20
                    item_c_data["passed"] = True
                    item_c_data["reason"] = "CII管制药品数据过滤、关联、排序完全准确无误"
                else:
                    item_c_data["reason"] = f"数据存在错误。预期行数 {len(golden_cii)}，实际行数 {len(agent_cii)}"
        except Exception as e:
            item_c_read["reason"] = f"读取异常: {e}"
    else:
        item_c_read["reason"] = "文件不存在"

    score_details.extend([item_c_read, item_c_data])
    total_score += item_c_read["score"] + item_c_data["score"]

    # Check 4: valid_tally.json (30 pts)
    tally_path = os.path.join(deliverables_dir, "valid_tally.json")
    item_t_read = {"item": "valid_tally.json 存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    item_t_data = {"item": "valid_tally.json 计算精准度", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    
    if os.path.exists(tally_path):
        try:
            with open(tally_path, 'r', encoding='utf-8') as f:
                agent_tally = json.load(f)
            item_t_read["score"] = 10
            item_t_read["passed"] = True
            item_t_read["reason"] = "合法的 JSON 文件"
            
            if agent_tally == golden_tally:
                item_t_data["score"] = 20
                item_t_data["passed"] = True
                item_t_data["reason"] = "有效非管控药品数量计算精准"
            else:
                item_t_data["reason"] = f"计算结果不匹配。预期 Key 数量 {len(golden_tally)}，实际 {len(agent_tally)}"
        except Exception as e:
            item_t_read["reason"] = f"解析 JSON 异常: {e}"
    else:
        item_t_read["reason"] = "文件不存在"
        
    score_details.extend([item_t_read, item_t_data])
    total_score += item_t_read["score"] + item_t_data["score"]

    # Output score report
    report = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
