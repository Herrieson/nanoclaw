import os
import json
import csv
import random
import string

def build_env():
    # 设定固定的随机种子，保证每次生成环境的结果一致（绝对逻辑可解）
    random.seed(1679)

    os.makedirs("state_registry", exist_ok=True)
    os.makedirs("disciplinary_actions", exist_ok=True)
    os.makedirs("school_submissions", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # ==========================================
    # 1. 构建州注册库 (State Registry)
    # ==========================================
    all_staff = []
    active_staff = set()
    expired_staff = set()

    # 生成 1000 个 staff_id
    for _ in range(1000):
        staff_id = "S-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        all_staff.append(staff_id)

    # 乱序并分配状态
    random.shuffle(all_staff)
    for i, staff_id in enumerate(all_staff):
        status = "Active" if i < 600 else "Expired"
        if status == "Active":
            active_staff.add(staff_id)
        else:
            expired_staff.add(staff_id)

    # 碎片化分布到不同地区目录下
    staff_idx = 0
    for region in range(1, 16):
        os.makedirs(f"state_registry/region_{region}", exist_ok=True)
        for part in range(1, 4):
            registry_data = []
            for _ in range(25):
                if staff_idx >= len(all_staff):
                    break
                sid = all_staff[staff_idx]
                registry_data.append({
                    "staff_id": sid,
                    "name": f"Name_{sid}",
                    "license_type": random.choice(["LPC", "LCSW", "LMFT", "PhD"]),
                    "issue_year": random.randint(2010, 2023),
                    "status": "Active" if sid in active_staff else "Expired"
                })
                staff_idx += 1
            
            with open(f"state_registry/region_{region}/registry_part_{part}.json", "w", encoding="utf-8") as f:
                json.dump(registry_data, f, indent=2)

    # ==========================================
    # 2. 构建纪律委员会日志 (Disciplinary Actions)
    # ==========================================
    # 挑选 50 个本来是 Active 的人进行吊销
    revoked_staff = set(random.sample(list(active_staff), 50))
    real_active_staff = active_staff - revoked_staff

    for i in range(1, 31):
        with open(f"disciplinary_actions/meeting_log_{i}.txt", "w", encoding="utf-8") as f:
            if i == 14:  # 这是带有真实线索的文件
                f.write("CONFIDENTIAL - DISCIPLINARY BOARD MEETING\n")
                f.write("Status: FINALIZED_OCT_2023\n")
                f.write("The following individuals have their licenses permanently revoked due to misconduct:\n\n")
                for r_sid in revoked_staff:
                    f.write(f" - REVOKED: {r_sid}\n")
                    f.write(f"   Reason: Code violation {random.randint(100,999)}\n")
            else:
                f.write(f"Routine meeting notes {i}...\n")
                f.write("Discussed budget and scheduling.\n")
                # 放入一些假的 REVOKED 干扰项（因为没有 FINALIZED_OCT_2023 关键字，不应被采纳）
                fake_revoked = random.sample(list(real_active_staff), 3)
                f.write("Pending investigations (NOT FINAL):\n")
                for fsid in fake_revoked:
                    f.write(f" - REVOKED: {fsid} (Awaiting Appeal)\n")

    # ==========================================
    # 3. 构建学校提交记录 (School Submissions)
    # ==========================================
    # 准备时长数据格式生成逻辑
    def generate_duration_string(minutes):
        choices = [
            str(minutes),
            f"{minutes}m",
            f"{minutes} mins",
            f"{minutes} minutes"
        ]
        if minutes % 60 == 0:
            h = minutes // 60
            choices.extend([f"{h}h", f"{h} hours", f"{h} hr"])
        elif minutes % 30 == 0:
            h = minutes / 60
            choices.extend([f"{h}h", f"{h} hours"])
        return random.choice(choices)

    # 生成 5000 条基础记录
    base_records = []
    session_id_counter = 100000

    for _ in range(5000):
        # 80% 的记录由真实合规者提供，10% 由被吊销者提供，10% 由过期/完全伪造者提供
        prob = random.random()
        if prob < 0.8:
            sid = random.choice(list(real_active_staff))
        elif prob < 0.9:
            sid = random.choice(list(revoked_staff))
        else:
            # Expired 或完全不存在的骗子
            sid = random.choice(list(expired_staff) + ["S-FAKE99", "S-SCAM00"])

        # 生成时长: 30, 45, 60, 90, 120 分钟
        real_minutes = random.choice([30, 45, 60, 90, 120])
        dur_str = generate_duration_string(real_minutes)
        
        base_records.append({
            "session_id": session_id_counter,
            "staff_id": sid,
            "duration": dur_str,
            "date": f"2023-10-{random.randint(1, 31):02d}"
        })
        session_id_counter += 1

    # 注入重复记录 (考察 session_id 去重能力)
    duplicates = random.sample(base_records, 300)
    all_records = base_records + duplicates
    random.shuffle(all_records)

    # 碎片化分布到不同学区
    record_idx = 0
    for district in range(1, 21):
        os.makedirs(f"school_submissions/district_{district}", exist_ok=True)
        for part in range(1, 6):
            chunk = []
            for _ in range(55): # 20 * 5 * 55 = 5500 > 5300
                if record_idx >= len(all_records):
                    break
                chunk.append(all_records[record_idx])
                record_idx += 1
            
            if not chunk:
                break

            # 一半存 JSON，一半存 CSV
            file_type = "json" if (district + part) % 2 == 0 else "csv"
            file_path = f"school_submissions/district_{district}/records_part_{part}.{file_type}"
            
            if file_type == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(chunk, f, indent=2)
            else:
                with open(file_path, "w", encoding="utf-8", newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=["session_id", "staff_id", "duration", "date"])
                    writer.writeheader()
                    writer.writerows(chunk)

if __name__ == "__main__":
    build_env()
