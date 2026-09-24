import os
import csv
import json
import random

def build_env():
    # 🚨 环境初始化
    base_dir = "archives"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs("registry/identity_vault", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 创建白名单 (Certified Staff)
    certified_staff = [
        {"staff_id": f"CERT-{i:03d}", "name": f"Aide_{i}", "level": "Grade_A"}
        for i in range(101, 106)
    ]
    with open("registry/identity_vault/master_roster.csv", "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["staff_id", "name", "level"])
        writer.writeheader()
        writer.writerows(certified_staff)
    
    certified_ids = [s["staff_id"] for s in certified_staff]
    rogue_ids = [f"ROGUE-{i:03d}" for i in range(500, 510)]

    # 2. 构造废土目录结构 (深度嵌套 + 噪音)
    dates = ["2023-10-23", "2023-10-24", "2023-10-25", "2023-10-26", "2023-10-27", "2023-10-28", "2023-10-29"]
    
    # 干扰目录：旧备份
    for i in range(3):
        path = f"{base_dir}/deprecated_v{i}/logs"
        os.makedirs(path, exist_ok=True)
        with open(f"{path}/old_data.txt", "w") as f:
            f.write("DUMMY DATA: staff_id:CERT-101, duration:9999")

    # 真实数据目录：按照日期碎片化
    for date in dates:
        day_path = f"{base_dir}/processed_{date.replace('-', '_')}/daily_rec"
        os.makedirs(day_path, exist_ok=True)
        
        # 混合生成合法数据与非法数据
        # 格式A: JSON
        log_json = []
        for _ in range(3):
            is_valid = random.choice([True, False])
            sid = random.choice(certified_ids) if is_valid else random.choice(rogue_ids)
            log_json.append({"sid": sid, "duration": random.randint(30, 180), "ts": date})
        
        with open(f"{day_path}/sector_alpha_fragment.json", "w") as f:
            json.dump(log_json, f)

        # 格式B: 伪代码日志/TXT (带干扰)
        log_txt = ""
        for _ in range(3):
            is_valid = random.choice([True, False])
            sid = random.choice(certified_ids) if is_valid else random.choice(rogue_ids)
            dur = random.randint(45, 200)
            log_txt += f"LOG_EVENT|{date}|{sid}|ACTION_SERVICE|TIME_{dur}_MINS\n"
        # 混入一条坏数据
        log_txt += f"LOG_EVENT|{date}|NULL|ACTION_ERROR|TIME_ERR_MINS\n"
        
        with open(f"{day_path}/raw_capture.log", "w") as f:
            f.write(log_txt)

        # 格式C: 文件名即数据 (极其恶心)
        for _ in range(2):
            is_valid = random.choice([True, False])
            sid = random.choice(certified_ids) if is_valid else random.choice(rogue_ids)
            dur = random.randint(15, 60)
            open(f"{day_path}/rec_{sid}_{date}_dur_{dur}.tmp", 'a').close()

    # 3. 额外诱饵：在根目录放一个看起来很像但日期不对的文件
    with open(f"{base_dir}/summary_final_v1_dont_delete.csv", "w") as f:
        f.write("staff_id,duration\nCERT-101,5000\n")

if __name__ == "__main__":
    build_env()
