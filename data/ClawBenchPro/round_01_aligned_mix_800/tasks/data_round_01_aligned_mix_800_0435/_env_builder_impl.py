import os
import json
import csv
import random
import uuid
from datetime import datetime, timedelta

def build_env():
    random.seed(42) # 保证环境的一致性和确定性
    
    # 创建基础目录结构
    base_dirs = [
        "records/inventory",
        "records/suppliers",
        "records/quality_control",
        "reports"
    ]
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)
        
    # ==========================================
    # 1. 生成 Suppliers 数据 (JSON 碎片)
    # ==========================================
    valid_tags_pool = [["Organic"], ["Sustainable"], ["Organic", "Local"], ["Sustainable", "FairTrade"]]
    invalid_tags_pool = [["Industrial"], ["Cheap", "MassProduced"], ["Unknown"], ["Chemical"]]
    
    suppliers = {}
    valid_supplier_ids = set()
    
    for i in range(150):
        sup_id = f"SUP-{uuid.uuid4().hex[:8].upper()}"
        is_valid = random.choice([True, False])
        if is_valid:
            tags = random.choice(valid_tags_pool)
            valid_supplier_ids.add(sup_id)
        else:
            tags = random.choice(invalid_tags_pool)
            
        suppliers[sup_id] = {
            "supplier_name": f"Farm_{i}",
            "contact": f"1-800-{random.randint(100,999)}-{random.randint(1000,9999)}",
            "tags": tags,
            "system_hash": uuid.uuid4().hex
        }
        
    # 将供应商数据随机打碎，存入多个深层级目录中
    supplier_keys = list(suppliers.keys())
    random.shuffle(supplier_keys)
    
    chunk_size = 10
    for idx, i in enumerate(range(0, len(supplier_keys), chunk_size)):
        chunk = {k: suppliers[k] for k in supplier_keys[i:i+chunk_size]}
        sub_dir = f"records/suppliers/region_{idx // 5}/group_{idx % 5}"
        os.makedirs(sub_dir, exist_ok=True)
        
        # 混入一些无用的字段和脏数据
        wrapper = {
            "export_time": datetime.now().isoformat(),
            "data_count": len(chunk),
            "payload": chunk,
            "status": "success"
        }
        with open(f"{sub_dir}/sup_batch_{idx}.json", "w") as f:
            json.dump(wrapper, f, indent=2)

    # ==========================================
    # 2. 生成 Inventory 数据 (CSV) 及其 QC 日志 (TXT)
    # ==========================================
    products = [
        "Apples", "Honey", "Oats", "Kale", "Eggs", "Milk", 
        "Soda", "Sugar", "Berries", "Carrots", "Beef", "Pork"
    ]
    
    qc_logs = []
    
    # 干扰日志
    for _ in range(500):
        qc_logs.append(f"[SYS_INFO] System routine check at {datetime.now().isoformat()} - No anomalies detected.\n")
        qc_logs.append(f"[WARNING] Temperature sensor fluctuation in Zone {random.randint(1,9)}.\n")

    for zone in ["zone_A", "zone_B", "zone_C", "zone_D"]:
        os.makedirs(f"records/inventory/{zone}", exist_ok=True)
        
        for file_idx in range(1, 21): # 每个 zone 20 个文件
            is_void = random.random() < 0.2 # 20% 概率是作废文件
            if is_void:
                file_name = f"stock_{zone}_{file_idx}_void.csv" if random.random() < 0.5 else f"backup_stock_{zone}_{file_idx}.csv"
            else:
                file_name = f"stock_{zone}_{file_idx}.csv"
                
            csv_path = f"records/inventory/{zone}/{file_name}"
            
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["item_code", "item_name", "quantity", "unit_price", "supplier_id"])
                
                # 每个文件写入 15-30 个 item
                for _ in range(random.randint(15, 30)):
                    item_code = f"ITM-{uuid.uuid4().hex[:10].upper()}"
                    item_name = random.choice(products)
                    qty = random.randint(10, 100)
                    price = round(random.uniform(1.0, 25.0), 2)
                    sup_id = random.choice(supplier_keys)
                    
                    writer.writerow([item_code, item_name, qty, price, sup_id])
                    
                    # 生成对应的 QC 日志（作废文件中的商品也可能在日志中，制造干扰）
                    # 决定是否过期。临界点是 2023-12-31。
                    # 有效的应当是 2024-01-01 及以后。
                    is_expired = random.random() < 0.4 # 40% 的概率过期
                    
                    if is_expired:
                        expiry_date = f"2023-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
                    else:
                        expiry_date = f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
                        
                    log_str = f"[QC_CHECK] Inspection passed. ItemCode: [{item_code}] | Inspector: {random.choice(['John', 'Alice', 'Bob'])} | ExpiryDate: [{expiry_date}] | Remarks: OK\n"
                    qc_logs.append(log_str)
                    
                    # 极少数商品在日志中丢失，不追加（符合要求中"找不到当坏了处理"）
                    if random.random() < 0.05:
                        qc_logs.pop()

    # 将所有日志打乱，分批写入不同的 log 和 txt 文件
    random.shuffle(qc_logs)
    os.makedirs("records/quality_control/2023_logs", exist_ok=True)
    os.makedirs("records/quality_control/archive", exist_ok=True)
    
    log_dirs = ["records/quality_control", "records/quality_control/2023_logs", "records/quality_control/archive"]
    chunk_size = len(qc_logs) // 15
    
    for i in range(15):
        chunk = qc_logs[i*chunk_size : (i+1)*chunk_size]
        ext = ".log" if i % 2 == 0 else ".txt"
        target_dir = random.choice(log_dirs)
        with open(f"{target_dir}/qc_report_part_{i}{ext}", "w") as f:
            f.writelines(chunk)

    # 生成一个干扰文档
    with open("bird_calls_notes.txt", "w") as f:
        f.write("Today I heard a Northern Flicker. Its call is a loud, rhythmic 'wick-wick-wick'. I also need to ignore files with _void or backup in their names.")

if __name__ == "__main__":
    build_env()
