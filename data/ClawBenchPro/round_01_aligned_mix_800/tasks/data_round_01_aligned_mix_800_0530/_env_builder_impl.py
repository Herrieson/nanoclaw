import os
import json
import csv
import random
from datetime import datetime

def build_env():
    # 设定随机种子以确保每次生成的数据和结果完全一致，保证绝对可解
    random.seed(42)

    # 创建复杂的废土目录结构
    dirs = [
        "auth_system/volunteers_db",
        "event_management/approved_rosters",
        "field_data/Sector_North",
        "field_data/Sector_South",
        "field_data/Sector_East",
        "field_data/Sector_West",
        "deliverables"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. 制造信息碎片化：生成用户数据库（包含Active和Inactive）
    volunteers = {}
    for i in range(1, 151):
        vid = f"VOL_{i:04d}"
        name = f"User_{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{i}"
        status = "Active" if random.random() > 0.3 else "Inactive"
        volunteers[vid] = {"id": vid, "name": name, "status": status}
    
    # 将用户数据打碎成 5 个 JSON 文件
    v_items = list(volunteers.values())
    chunk_size = 30
    for idx in range(5):
        chunk = v_items[idx*chunk_size : (idx+1)*chunk_size]
        with open(f"auth_system/volunteers_db/db_shard_{idx}.json", "w") as f:
            json.dump({"data": chunk, "shard_id": idx, "version": "v1.2"}, f)

    # 2. 制造逻辑多段依赖：生成活动报名审批名单
    # 随机选 80 个人作为本次活动的 approved
    approved_ids = random.sample(list(volunteers.keys()), 80)
    with open("event_management/approved_rosters/eco_cleanup_2023.txt", "w") as f:
        f.write("# OFFICIAL APPROVED ROSTER FOR ECO CLEANUP 2023\n")
        f.write("# ONLY these IDs are allowed to participate if they are ACTIVE in DB.\n\n")
        for vid in approved_ids:
            f.write(f"{vid}\n")

    # 明确计算真正的白名单 (Active 且 Approved) 留作后面生成干扰项使用
    true_whitelist_ids = {vid for vid in approved_ids if volunteers[vid]["status"] == "Active"}
    suspect_pool_ids = set(volunteers.keys()) - true_whitelist_ids

    # 3. 规模压制 & 噪音：生成现场数据文件
    sectors = ["Sector_North", "Sector_South", "Sector_East", "Sector_West"]
    
    def generate_time_pair(hours):
        # 随机生成当天的开始和结束时间
        start_hour = random.randint(6, 18)
        start_min = random.randint(0, 59)
        end_total_mins = start_hour * 60 + start_min + int(hours * 60)
        end_hour = end_total_mins // 60
        end_min = end_total_mins % 60
        # 边界处理，超过午夜折算为 23:59（简化题意不考虑跨天，生成的数据保证在同一天）
        if end_hour > 23:
            end_hour, end_min = 23, 59
        return f"{start_hour:02d}:{start_min:02d}", f"{end_hour:02d}:{end_min:02d}"

    def write_csv_tsv(filepath, records, sep=","):
        with open(filepath, "w", newline='') as f:
            writer = csv.writer(f, delimiter=sep)
            writer.writerow(["date", "volunteer_id", "volunteer_name", "start_time", "end_time"])
            for r in records:
                writer.writerow(r)

    def write_log(filepath, records):
        with open(filepath, "w") as f:
            f.write("--- FIELD SYSTEM LOG DUMP ---\n")
            for r in records:
                date, vid, name, mins = r
                f.write(f"[{date}] ID: {vid} | Name: {name} => Duration: {mins} mins recorded.\n")

    # 遍历生成 50 个文件
    for file_idx in range(50):
        sector = random.choice(sectors)
        is_invalid_file = random.random() < 0.25 # 25% 概率是干扰废弃文件
        
        if is_invalid_file:
            prefix = random.choice(["draft_", "rejected_", "backup_"])
        else:
            prefix = "verified_"
            
        file_ext = random.choice([".csv", ".tsv", ".log"])
        filename = f"{prefix}record_{file_idx:03d}{file_ext}"
        filepath = os.path.join("field_data", sector, filename)

        records_csv = []
        records_log = []
        
        # 每个文件生成 10~30 条记录
        num_records = random.randint(10, 30)
        for _ in range(num_records):
            # 80% 概率是真白名单，20% 概率是嫌疑人
            if random.random() < 0.8 and true_whitelist_ids:
                vid = random.choice(list(true_whitelist_ids))
            else:
                vid = random.choice(list(suspect_pool_ids))
            
            name = volunteers[vid]["name"]
            
            # 工时情况：90% 正常 (1~8小时), 10% 异常 (>12小时)
            if random.random() < 0.9:
                hours = random.uniform(1.0, 8.0)
            else:
                hours = random.uniform(12.5, 20.0)
                
            date_str = f"2023-10-{random.randint(10, 15)}"
            
            if file_ext in [".csv", ".tsv"]:
                st, et = generate_time_pair(hours)
                records_csv.append([date_str, vid, name, st, et])
            else:
                mins = int(hours * 60)
                records_log.append([date_str, vid, name, mins])
                
        if file_ext == ".csv":
            write_csv_tsv(filepath, records_csv, sep=",")
        elif file_ext == ".tsv":
            write_csv_tsv(filepath, records_csv, sep="\t")
        elif file_ext == ".log":
            write_log(filepath, records_log)

if __name__ == "__main__":
    build_env()
