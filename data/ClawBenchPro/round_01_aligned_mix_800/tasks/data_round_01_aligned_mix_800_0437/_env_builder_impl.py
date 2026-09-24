import os
import random
import json
import yaml
from datetime import datetime

def build_env():
    # 🚨 约定：cwd 为 assets/data_round_01_aligned_mix_800_0437/
    base_dir = "case_archives"
    output_dir = "audit_report"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # 核心元数据
    families = ["Kim", "Garcia", "Smith", "Chen", "Lee", "Patel", "Muller", "Wong", "Baker", "Zucker"]
    keywords = ["Housing Instability", "Child Safety", "Routine Check", "Job Loss", "Medical Emergency"]
    
    # 1. 制造深层嵌套和碎片化
    # 结构：case_archives/{sub_dir}/{id}_{timestamp}_{version}.{ext}
    
    for i in range(200):  # 生成 200 个碎片文件
        case_id = f"CS_{random.randint(100, 120):03d}" # 只有 20 个独立 ID，产生大量冲突和版本
        family = families[int(case_id[-2:]) % len(families)]
        score = random.randint(10, 90)
        date_year = random.choice([2023, 2024, 2025, 2026]) # 包含无效日期
        date_str = f"{date_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        note = random.choice(keywords)
        version = random.randint(1, 5)
        
        # 随机路径
        sub_folder = random.choice(["active_logs", "temp_shards", "legacy_backups", "unprocessed"])
        os.makedirs(os.path.join(base_dir, sub_folder), exist_ok=True)
        
        # 随机格式
        ext = random.choice(["json", "txt", "yaml", "log"])
        timestamp = f"202401{random.randint(10,30):02d}"
        file_name = f"{case_id}_T{timestamp}_V{version}.{ext}"
        
        # 故意制造干扰：有些文件是过时的
        if "legacy" in sub_folder or version < 3:
            file_name = "DEPRECATED_" + file_name
        
        file_path = os.path.join(base_dir, sub_folder, file_name)
        
        # 写入异构数据
        data = {"id": case_id, "family": family, "score": score, "date": date_str, "notes": note}
        
        if ext == "json":
            with open(file_path, "w") as f:
                json.dump(data, f)
        elif ext == "yaml":
            with open(file_path, "w") as f:
                yaml.dump(data, f)
        elif ext == "log":
            with open(file_path, "w") as f:
                f.write(f"ENTRY_START | ID:{case_id} | FAM:{family} | SCORE:{score} | DATE:{date_str} | MSG:{note} | ENTRY_END")
        else: # txt
            with open(file_path, "w") as f:
                f.write(f"Record for {case_id}\nFamily: {family}\nScore: {score}\nDate: {date_str}\nNotes: {note}")

    # 2. 注入唯一性提示线索文件
    with open(os.path.join(base_dir, "processing_rules.schema"), "w") as f:
        f.write("CRITICAL: Only files WITHOUT 'DEPRECATED' prefix are valid.\n")
        f.write("CRITICAL: If multiple versions exist for the same ID, use the one with the highest V(ersion) number.\n")
        f.write("CRITICAL: Current audit boundary: Year < 2025.")

    # 3. 填充大量噪音文件
    for j in range(50):
        noise_path = os.path.join(base_dir, f"sys_dump_{j}.tmp")
        with open(noise_path, "w") as f:
            f.write("0x" + "FF"*100)

if __name__ == "__main__":
    build_env()
