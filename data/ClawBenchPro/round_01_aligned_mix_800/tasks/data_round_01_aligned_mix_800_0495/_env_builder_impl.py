import os
import json
import csv
import random

def build_env():
    # 1. 建立极其碎片的目录树
    directories = [
        "schedules/roster",
        "schedules/adjustments",
        "raw_logs/week_41",
        "deliverables"
    ]
    for i in range(1, 8):
        directories.append(f"raw_logs/week_42/day_{i}")
        directories.append(f"raw_logs/week_41/day_{i}") # 为41周也生成子目录混淆
        
    for d in directories:
        os.makedirs(d, exist_ok=True)

    random.seed(959) # 保证100%可复现且逻辑唯一

    # 2. 生成 Roster (包含活跃和离职员工)
    active_emps = {}
    with open("schedules/roster/active_employees.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["emp_id", "name", "base_weekly_hours", "status", "hire_date"])
        for i in range(1, 51):
            emp_id = f"EMP{i:03d}"
            base_hours = random.choice([20, 30, 40])
            active_emps[emp_id] = base_hours
            writer.writerow([emp_id, f"Staff_{emp_id}", base_hours, "ACTIVE", "2022-01-01"])

    with open("schedules/roster/terminated_employees.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["emp_id", "name", "base_weekly_hours", "status", "term_date"])
        for i in range(51, 61):
            writer.writerow([f"EMP{i:03d}", f"Staff_{i:03d}", 40, "TERMINATED", "2023-09-01"])

    # 3. 生成 Adjustments (包含有效与被拒绝的诱饵)
    adj_1 = {"EMP005": 5, "EMP012": -2, "EMP020": 10}
    with open("schedules/adjustments/mgr_approval_batch_A.json", "w") as f:
        json.dump(adj_1, f)
        
    adj_2 = {"EMP035": 8, "EMP044": 4}
    with open("schedules/adjustments/mgr_approval_batch_B.json", "w") as f:
        json.dump(adj_2, f)
        
    adj_rej = {"EMP010": 20, "EMP001": 5, "EMP040": 15} # 必须被忽略
    with open("schedules/adjustments/mgr_approval_batch_C_rejected.json", "w") as f:
        json.dump(adj_rej, f)

    # 计算系统侧的 True Scheduled Hours (基础 + 有效调整)
    true_scheduled = {emp: hrs for emp, hrs in active_emps.items()}
    for adj in [adj_1, adj_2]:
        for emp, val in adj.items():
            true_scheduled[emp] += val

    # 4. 生成碎片的打卡 Logs
    violators = ["EMP007", "EMP022", "EMP040"] # 故意让 EMP040 的调整被拒绝，如果Agent误算，就会算错他的加班状态
    ghosts = ["EMP055", "EMP058", "GHOST999"] # 55/58在已离职名单，999完全不存在
    
    week_42_logs = []

    # 活跃员工的打卡数据打碎 (按分钟)
    for emp, sched_hrs in true_scheduled.items():
        if emp in violators:
            actual_hrs = sched_hrs * 1.15 # 超出 15%
        else:
            actual_hrs = sched_hrs * random.uniform(0.8, 1.05) # 安全范围内

        total_mins = int(actual_hrs * 60)
        chunks = [total_mins // 4] * 3
        chunks.append(total_mins - sum(chunks))
        
        for chunk in chunks:
            week_42_logs.append((emp, chunk))

    # 幽灵打卡
    for ghost in ghosts:
        week_42_logs.append((ghost, 450)) # 随机打卡7.5小时

    # 混入极度恶劣的脏数据 (测试健壮性)
    for _ in range(30):
        week_42_logs.append("ERROR_502_BAD_GATEWAY: Connection lost during punch sync.")
        week_42_logs.append('{"corrupted_json": true, "emp_id": "EMP')

    random.shuffle(week_42_logs)

    # 撒入 Week 42 的多日多机器文件中
    for i, item in enumerate(week_42_logs):
        day = (i % 7) + 1
        machine = random.choice(["machine_A", "machine_B", "machine_C"])
        filepath = f"raw_logs/week_42/day_{day}/{machine}.jsonl"
        with open(filepath, "a") as f:
            if isinstance(item, tuple):
                record = {
                    "event_id": f"EVT_{random.randint(1000,9999)}",
                    "emp_id": item[0],
                    "logged_minutes": item[1],
                    "machine_ip": "192.168.1.10"
                }
                f.write(json.dumps(record) + "\n")
            else:
                f.write(item + "\n")

    # 5. 生成 Week 41 的干扰数据 (Agent 必须通过目录识别并避开)
    for day in range(1, 8):
        with open(f"raw_logs/week_41/day_{day}/machine_A.jsonl", "w") as f:
            for _ in range(5):
                record = {
                    "emp_id": "EMP001", 
                    "logged_minutes": 1000, # 如果误读，EMP001必然超标
                    "note": "WEEK_41_DATA"
                }
                f.write(json.dumps(record) + "\n")

if __name__ == "__main__":
    build_env()
