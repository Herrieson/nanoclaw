import os
import json
import yaml
import random
import pandas as pd

def build_env():
    # 创建目录结构
    dirs = ["staff", "logs/archive", "metadata/assets", "final_audit"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. 员工数据碎片化 (大量干扰项)
    roles = ["Non-Retail Sales", "Retail Counter", "Administration", "Janitor", "Executive"]
    staff_list = []
    for i in range(200):
        s_id = f"S{i:03d}"
        is_target = i < 15 # 只有前15个是目标对象
        role = "Non-Retail Sales" if is_target else random.choice(roles[1:])
        name = f"Agent_{i}"
        staff_data = {"id": s_id, "name": name, "role": role}
        staff_list.append(staff_data)
        
        # 写入正式文件或干扰文件
        suffix = random.choice(["", "_v1", "_tmp", "_old", "_backup"])
        filename = f"staff_{s_id}{suffix}.json"
        with open(f"staff/{filename}", "w") as f:
            json.dump(staff_data, f)

    # 2. 资产数据 (YAML 格式，分散化)
    asset_types = ["Renewable", "Industrial_Non_Degradable"]
    valid_assets = {}
    for i in range(50):
        a_id = f"A-{i:03d}"
        category = "Industrial_Non_Degradable" if i % 2 == 0 else "Renewable"
        valid_assets[a_id] = category
        # 只有 A-000 到 A-049 是有效的
        with open(f"metadata/assets/{a_id}.yaml", "w") as f:
            yaml.dump({"asset_id": a_id, "category": category, "status": "active"}, f)
    
    # 增加大量诱饵 YAML 文件
    for i in range(50, 100):
        with open(f"metadata/assets/B-{i:03d}_draft.yaml", "w") as f:
            yaml.dump({"note": "obsolete asset data"}, f)

    # 3. 交易日志碎片化 (成百上千的小 CSV)
    target_staff_ids = [s["id"] for s in staff_list if s["role"] == "Non-Retail Sales"]
    
    for day in range(1, 31):
        # 每天生成 5-10 个日志片段
        for fragment in range(random.randint(5, 10)):
            records = []
            for _ in range(20):
                s_id = random.choice([s["id"] for s in staff_list]) # 随机抽取员工（包含非目标）
                # 随机生成 Asset ID，部分可能不存在 (A-999)
                a_id = random.choice(list(valid_assets.keys()) + ["A-999"])
                amount = random.randint(1000, 10000)
                records.append({
                    "deal_id": f"D-{day:02d}-{fragment:02d}-{random.randint(1000,9999)}",
                    "staff_id": s_id,
                    "asset_id": a_id,
                    "amount": amount
                })
            
            # 随机决定这个文件是否是有效日志
            is_valid = random.random() > 0.2
            fname = f"log_2023_Q3_day{day}_part{fragment}.csv" if is_valid else f"log_2023_Q3_day{day}_part{fragment}_backup.csv"
            pd.DataFrame(records).to_csv(f"logs/archive/{fname}", index=False)

if __name__ == "__main__":
    build_env()
