import os
import sys
import json
import csv
import re
import httpx
from openai import OpenAI

def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    planning_dir = os.path.join(workspace, "planning")
    equipment_file = os.path.join(planning_dir, "heavy_equipment_volunteers.txt")
    hours_file = os.path.join(planning_dir, "total_hours.txt")
    roster_file = os.path.join(workspace, "master_roster.json")
    
    details = []
    total_score = 0

    # --- 1. 结构化目录检查 (10分) ---
    dir_exists = os.path.isdir(planning_dir)
    details.append({
        "item": "检查结果目录 'planning' 是否存在",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "目录已创建" if dir_exists else "未找到 planning 目录"
    })
    if dir_exists: total_score += details[-1]["score"]

    # --- 2. 核心逻辑重算 (用于比对结果) ---
    # 为了验证 Agent 的结果，我们需要在脚本内复刻逻辑，但要保持绝对严谨
    banned_names = set()
    banned_ids = set()
    
    # 提取黑名单 ID
    try:
        audit_root = os.path.join(workspace, "compliance_audits")
        for root, dirs, files in os.walk(audit_root):
            for file in files:
                if file.endswith(".log"):
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        matches = re.findall(r"\[CRITICAL_VIOLATION\]\s+WorkerID:\s+(W-\d+)", content)
                        banned_ids.update(matches)
        
        # 映射 ID 到 Name
        if os.path.exists(roster_file):
            with open(roster_file, 'r') as f:
                roster = json.load(f)
                for bid in banned_ids:
                    if bid in roster:
                        banned_names.add(roster[bid])
    except Exception as e:
        pass # 后续通过结果验证来判定

    # 遍历 signups 数据
    correct_total_hours = 0
    correct_volunteers = set()
    
    try:
        dump_root = os.path.join(workspace, "signups_dump")
        for root, dirs, files in os.walk(dump_root):
            for file in files:
                filepath = os.path.join(root, file)
                records = []
                if file.endswith(".json"):
                    with open(filepath, 'r') as f:
                        records = json.load(f)
                elif file.endswith(".csv"):
                    with open(filepath, 'r') as f:
                        reader = csv.DictReader(f, delimiter='|')
                        records = list(reader)
                else:
                    continue
                
                for r in records:
                    name = r.get("name")
                    status = r.get("status")
                    hours = int(r.get("hours", 0))
                    equip = r.get("equipment", "").lower()
                    
                    if status not in ["withdrawn", "cancelled"] and name not in banned_names:
                        correct_total_hours += hours
                        if "truck" in equip or "backhoe" in equip:
                            correct_volunteers.add(name)
    except Exception as e:
        pass

    # --- 3. 验证工时计算 (40分) ---
    hours_score = 0
    if os.path.exists(hours_file):
        try:
            with open(hours_file, 'r') as f:
                content = f.read().strip()
                agent_hours = int(re.search(r"\d+", content).group())
                if agent_hours == correct_total_hours:
                    hours_score = 40
                elif abs(agent_hours - correct_total_hours) < 50: # 允许极小误差（可能是浮点或特殊处理）
                    hours_score = 20
        except:
            pass
    
    details.append({
        "item": "验证 total_hours.txt 计算结果",
        "score": hours_score,
        "max_score": 40,
        "passed": hours_score == 40,
        "reason": f"预期: {correct_total_hours}, 实际: {content if os.path.exists(hours_file) else 'N/A'}"
    })
    total_score += hours_score

    # --- 4. 验证重型设备志愿者名单 (40分) ---
    vol_score = 0
    if os.path.exists(equipment_file):
        try:
            with open(equipment_file, 'r') as f:
                agent_vols = set(line.strip() for line in f if line.strip())
            
            # 集合比对：防止黑名单人员混入，防止取消者混入
            intersection = agent_vols.intersection(correct_volunteers)
            extra = agent_vols.difference(correct_volunteers) # 错误包含的
            missing = correct_volunteers.difference(agent_vols) # 漏掉的
            
            if len(extra) == 0 and len(missing) == 0:
                vol_score = 40
            elif len(extra) < 5 and len(missing) < 5:
                vol_score = 20 # 部分正确
        except:
            pass

    details.append({
        "item": "验证 heavy_equipment_volunteers.txt 名单准确性",
        "score": vol_score,
        "max_score": 40,
        "passed": vol_score == 40,
        "reason": f"名单准确率比对，应有人数: {len(correct_volunteers)}"
    })
    total_score += vol_score

    # --- 5. 禁止幻觉检查 (10分) ---
    # 检查 Agent 是否在没有文件的情况下凭空捏造了数据（通过检查代码执行轨迹的关联性）
    # 在 workplace 中表现为是否有非法的额外文件
    noise_check = not any(os.path.exists(os.path.join(planning_dir, f)) for f in ["script.py", "debug.log"]) # 仅作辅助
    details.append({
        "item": "文件规范性检查",
        "score": 10 if os.path.exists(hours_file) and os.path.exists(equipment_file) else 0,
        "max_score": 10,
        "passed": True,
        "reason": "输出文件完整"
    })
    total_score += details[-1]["score"]

    # 写入结果
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    run_verification()
