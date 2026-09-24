import os
import sys
import json
import csv
import glob
from pathlib import Path

def calculate_ground_truth(workspace):
    """
    根据 env_builder 的逻辑，在评测脚本中重新计算正确答案，作为基准。
    注意：由于 env_builder 使用了 random，验证脚本必须实时解析原始碎片数据。
    """
    roster = {}
    # 1. 解析 Roster
    roster_path = os.path.join(workspace, "registry/shards/roster_shard_*.json")
    for shard in glob.glob(roster_path):
        with open(shard, 'r') as f:
            data = json.load(f)
            roster[data['id']] = data['name']
    
    user_seconds = {uid: 0 for uid in roster.keys()}
    
    # 2. 解析数据碎片
    archive_root = os.path.join(workspace, "shadow_archive")
    
    # 定义合规目录（排除 deprecated）
    valid_dirs = [archive_root, os.path.join(archive_root, "node_alpha"), os.path.join(archive_root, "node_beta")]
    
    for v_dir in valid_dirs:
        if not os.path.exists(v_dir): continue
        
        # .log files (Pipe-separated: ID|Duration|Timestamp)
        for log_file in glob.glob(os.path.join(v_dir, "*.log")):
            with open(log_file, 'r') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        uid, dur = parts[0], parts[1]
                        if uid in roster:
                            try:
                                d_val = float(dur)
                                if d_val > 0: user_seconds[uid] += d_val
                            except: pass

        # .tmp files (JSON: [{"uid":..., "duration":...}])
        for tmp_file in glob.glob(os.path.join(v_dir, "*.tmp")):
            with open(tmp_file, 'r') as f:
                try:
                    data = json.load(f)
                    for entry in data:
                        uid, dur = entry.get('uid'), entry.get('duration')
                        if uid in roster:
                            try:
                                d_val = float(dur)
                                if d_val > 0: user_seconds[uid] += d_val
                            except: pass
                except: pass

        # .archive files (CSV: ID,Seconds)
        for arc_file in glob.glob(os.path.join(v_dir, "*.archive")):
            with open(arc_file, 'r') as f:
                reader = csv.reader(f)
                next(reader, None) # skip header
                for row in reader:
                    if len(row) >= 2:
                        uid, dur = row[0], row[1]
                        if uid in roster:
                            try:
                                d_val = float(dur)
                                if d_val > 0: user_seconds[uid] += d_val
                            except: pass

    # 计算最终报表
    truth = {}
    for uid, name in roster.items():
        hours = round(user_seconds[uid] / 3600, 2)
        status = "Active" if hours > 0 else "Inactive"
        truth[name] = {"hours": hours, "status": status}
    return truth

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    report_path = os.path.join(workspace, "deliverables/final_report.csv")

    # Item 1: 文件存在性 (10分)
    if os.path.exists(report_path):
        score_details.append({"item": "Final report existence", "score": 10, "max_score": 10, "passed": True, "reason": "Found deliverables/final_report.csv"})
        total_score += 10
    else:
        score_details.append({"item": "Final report existence", "score": 0, "max_score": 10, "passed": False, "reason": "Missing deliverables/final_report.csv"})
        # 如果文件不存在，后续无法进行，直接写入结果
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    # Item 2: 格式检查与解析 (20分)
    agent_data = {}
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # 检查列名是否正确
            expected_headers = ["Name", "Total_Hours", "Status"]
            if all(h in reader.fieldnames for h in expected_headers):
                score_details.append({"item": "CSV Headers", "score": 10, "max_score": 10, "passed": True, "reason": "Headers match requirement"})
                total_score += 10
            else:
                score_details.append({"item": "CSV Headers", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_headers}, got {reader.fieldnames}"})
            
            for row in reader:
                agent_data[row["Name"]] = {
                    "hours": float(row["Total_Hours"]),
                    "status": row["Status"]
                }
        score_details.append({"item": "CSV Content Parseable", "score": 10, "max_score": 10, "passed": True, "reason": "Content successfully parsed"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "CSV Content Parseable", "score": 0, "max_score": 20, "passed": False, "reason": f"Failed to parse CSV: {e}"})

    # Item 3: 数据准确性比对 (60分)
    truth = calculate_ground_truth(workspace)
    if agent_data:
        correct_entries = 0
        total_entries = len(truth)
        
        for name, data in truth.items():
            if name in agent_data:
                # 允许 0.01 的浮点误差，以防舍入逻辑差异
                if abs(agent_data[name]["hours"] - data["hours"]) <= 0.01 and agent_data[name]["status"] == data["status"]:
                    correct_entries += 1
        
        accuracy_score = int((correct_entries / total_entries) * 60)
        total_score += accuracy_score
        score_details.append({
            "item": "Data Accuracy (Strict Matching)",
            "score": accuracy_score,
            "max_score": 60,
            "passed": accuracy_score == 60,
            "reason": f"Matched {correct_entries}/{total_entries} users correctly. Check if 'deprecated' folder was correctly ignored."
        })

    # Item 4: 非法数据清洗检查 (10分)
    # 检查是否有 Ghost User (USR-001) 的记录，且由于 env_builder 中该用户没有分配有效 session，其 status 应该是 Inactive
    ghost_user_name = "Ghost User"
    if ghost_user_name in agent_data:
        if agent_data[ghost_user_name]["status"] == "Inactive" and agent_data[ghost_user_name]["hours"] == 0:
            score_details.append({"item": "Clean Data Handling", "score": 10, "max_score": 10, "passed": True, "reason": "Ghost User correctly identified as Inactive/0.00"})
            total_score += 10
        else:
            score_details.append({"item": "Clean Data Handling", "score": 0, "max_score": 10, "passed": False, "reason": "Ghost User incorrectly calculated; possible noise leakage."})
    else:
        score_details.append({"item": "Clean Data Handling", "score": 0, "max_score": 10, "passed": False, "reason": "Ghost User missing from report."})

    # 写入结果
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)

if __name__ == "__main__":
    verify()
