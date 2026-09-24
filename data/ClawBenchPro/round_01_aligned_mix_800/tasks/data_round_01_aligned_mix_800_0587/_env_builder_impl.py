import os
import random
import json
import hashlib
from datetime import datetime, timedelta

def build_env():
    # 🚨 这里的当前目录已经是 assets/data_round_01_aligned_mix_800_0587/
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("archive/meta/mapping", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. 核心白名单 (Legal Names)
    roster = ["Mateo Hernandez", "Santiago Garcia", "Luis Rodriguez", "Carlos Martinez", "Juan Lopez"]
    with open("master_roster.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(roster))

    # 2. 生成身份映射表 (UID to Name) - 散布在多个小 JSON 中
    uids = {f"ID-{1000+i}": name for i, name in enumerate(roster)}
    # 增加两个幽灵工人 UID
    ghosts = {"ID-9999": "Ghost_1", "ID-8888": "Ghost_2"}
    
    all_uids = {**uids, **ghosts}
    for uid, name in all_uids.items():
        sub_dir = f"archive/meta/mapping/{uid[:4]}"
        os.makedirs(sub_dir, exist_ok=True)
        with open(os.path.join(sub_dir, f"{uid}.json"), "w") as f:
            json.dump({"uid": uid, "real_identity": name}, f)

    # 3. 生成海量日志文件 (碎片化 + 噪音)
    # 规则：合法的日志文件名必须包含 'REAL' 字符串，且内容以 'LOG_v2' 开头
    start_date = datetime(2023, 10, 1)
    
    # 真实数据条目
    real_data = [
        {"uid": "ID-1000", "h": 8, "p": 2, "lang": "en"}, # Mateo
        {"uid": "ID-1001", "h": 12, "p": 1, "lang": "es"}, # Santiago
        {"uid": "ID-1002", "h": 10, "p": 0, "lang": "en"}, # Luis
        {"uid": "ID-9999", "h": 5, "p": 5, "lang": "en"}, # Ghost
        {"uid": "ID-1003", "h": 4, "p": 3, "lang": "es"}, # Carlos
        {"uid": "ID-1004", "h": 6, "p": 0, "lang": "mix"}, # Juan
        {"uid": "ID-1000", "h": 2, "p": 1, "lang": "en"}  # Mateo extra
    ]

    # 生成 1000 个干扰文件
    for i in range(1000):
        noise_name = f"raw_logs/backup_{hashlib.md5(str(i).encode()).hexdigest()}.tmp"
        with open(noise_name, "w") as f:
            f.write(f"Garbage data {random.random()}\nSTATUS: CORRUPTED")

    # 生成真实的碎片日志
    templates = {
        "en": "LOG_v2\nWorker UID: {uid}, Shift: {h} hours, Damage: {p} pillars",
        "es": "LOG_v2\nUID del Trabajador: {uid}, Turno: {h} horas, Pilares rotos: {p}",
        "mix": "LOG_v2\nID: {uid} | Time: {h}h | Roto: {p}"
    }

    for idx, entry in enumerate(real_data):
        timestamp = (start_date + timedelta(hours=idx)).strftime("%Y%m%d_%H%M")
        filename = f"raw_logs/REAL_SITE_LOG_{timestamp}_{idx}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            content = templates[entry['lang']].format(uid=entry['uid'], h=entry['h'], p=entry['p'])
            f.write(content)

    # 额外干扰：非 REAL 开头的类似文件
    with open("raw_logs/FAKE_SITE_LOG_20231001.txt", "w") as f:
        f.write("LOG_v2\nWorker UID: ID-1000, Shift: 999 hours, Damage: 999 pillars")

if __name__ == "__main__":
    build_env()
