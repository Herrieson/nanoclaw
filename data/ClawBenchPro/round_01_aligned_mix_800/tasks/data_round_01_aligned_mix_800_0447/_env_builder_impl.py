import os
import csv
import json
import random
import math

def build_env():
    random.seed(42) # 保证每次生成的废土数据一致，确保评测确定性

    # 1. 建立基础目录
    os.makedirs("baptism_records", exist_ok=True)
    os.makedirs("summary", exist_ok=True)
    base_raw_dir = "raw_records/2023/10"
    
    # 2. 生成受洗记录 (ID to Name 映射) - 500 名教徒
    all_baptized = []
    anime_surnames = ["Sato", "Tanaka", "Suzuki", "Takahashi", "Watanabe", "Uchiha", "Uzumaki", "Ayanami", "Ikari", "Zoldyck"]
    anime_firstnames = ["Kenji", "Hana", "Ichiro", "Yuki", "Ken", "Madara", "Naruto", "Rei", "Shinji", "Killua"]
    
    for i in range(1, 501):
        vid = f"V{i:04d}"
        name = f"{random.choice(anime_surnames)} {random.choice(anime_firstnames)}_{i}"
        all_baptized.append({"id": vid, "name": name, "baptized_date": f"202{random.randint(0,3)}-0{random.randint(1,9)}-1{random.randint(0,9)}"})
    
    # 将其打碎成 10 个 JSON 碎片
    random.shuffle(all_baptized)
    chunk_size = 50
    for chunk_idx in range(10):
        chunk = all_baptized[chunk_idx*chunk_size : (chunk_idx+1)*chunk_size]
        with open(f"baptism_records/shard_{chunk_idx:03d}.json", "w", encoding="utf-8") as f:
            json.dump({"records": chunk}, f, indent=2)

    # 3. 创建白名单 CSV (选取其中 300 人作为白名单)
    whitelist_baptized = all_baptized[:300]
    whitelist_ids = [p["id"] for p in whitelist_baptized]
    with open("official_whitelist.csv", "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["volunteer_id"])
        for vid in whitelist_ids:
            writer.writerow([vid])

    # 用于外部干扰的纯路人名
    outsiders = ["Monkey D Luffy", "Roronoa Zoro", "Saitama", "Eren Yeager", "Levi Ackerman"]

    # 4. 生成 31 天的废土记录
    for day in range(1, 32):
        day_dir = os.path.join(base_raw_dir, f"{day:02d}")
        os.makedirs(day_dir, exist_ok=True)

        # 干扰文件 1: 旧备份
        with open(os.path.join(day_dir, f"attendance_{day:02d}.log.bak"), "w", encoding="utf-8") as f:
            f.write("[VALID] Name: \"Fake Person\" | Hours: 99.0\n")
        
        # 干扰文件 2: 动漫/哲学随笔
        with open(os.path.join(day_dir, "notes.txt"), "w", encoding="utf-8") as f:
            f.write("Existence precedes essence...\n")
            f.write("I mustn't run away, I mustn't run away!\n")

        # 干扰文件 3: 格式错误的无关日志
        with open(os.path.join(day_dir, "system_cache.log"), "w", encoding="utf-8") as f:
            f.write("[WARN] System rebooting...\n")
            f.write(f"[VOID] ID: V9999 - Duration: 5.5H\n")

        # 真实日志文件
        log_filename = f"daily_attendance_{random.randint(100,999)}.log"
        with open(os.path.join(day_dir, log_filename), "w", encoding="utf-8") as f:
            # 每天生成 30 条记录
            for _ in range(30):
                is_valid = random.choice([True, True, True, False]) # 25% 概率作废
                status_str = random.choice(["[OK]", "[VALID]"]) if is_valid else random.choice(["[VOID]", "[CANCELLED]"])
                
                hours = round(random.uniform(1.0, 8.0), 1)
                
                # 决定身份类型: 60% 白名单, 30% 受洗但非白名单, 10% 纯路人
                identity_roll = random.random()
                if identity_roll < 0.6:
                    person = random.choice(whitelist_baptized)
                elif identity_roll < 0.9:
                    person = random.choice(all_baptized[300:])
                else:
                    person = {"id": None, "name": random.choice(outsiders)}

                # 决定记录格式: 用 ID 还是用 Name
                if person["id"] is not None and random.choice([True, False]):
                    # 格式1: 带有 ID
                    f.write(f"{status_str} ID: {person['id']} - Duration: {hours}H\n")
                else:
                    # 格式2: 带有 Name
                    f.write(f"{status_str} Name: \"{person['name']}\" | Hours: {hours}\n")
                
                # 混入一些无意义的噪音行
                if random.random() < 0.1:
                    f.write(f"--- noise data timestamp {random.randint(1000,9999)} ---\n")

if __name__ == "__main__":
    build_env()
