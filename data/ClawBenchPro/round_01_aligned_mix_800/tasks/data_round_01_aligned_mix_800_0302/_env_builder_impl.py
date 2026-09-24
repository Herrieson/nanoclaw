import os
import json
import base64

def build_env():
    # 创建目录
    os.makedirs("warehouse_reports", exist_ok=True)
    os.makedirs("accounting", exist_ok=True)

    # 降维改造：将原本的 CSV 转换为模拟的 RFID 密文数据 .dat 文件
    dat_file = "warehouse_reports/inventory_log_a.dat"
    # 这是 Agent 必须通过 Decoder 解析出的底层真实数据，包含噪音和重复
    rfid_data = [
        {"batch_id": "B001", "mineral": "Copper", "weight_kg": "1200", "purity_pct": "88.5%"},
        {"batch_id": "B002", "mineral": "Nickel", "weight_kg": "500", "purity_pct": "82.0"},  # 不合格
        {"batch_id": "B003", "mineral": "Zinc", "weight_kg": "2000kg", "purity_pct": "91"},
        {"batch_id": "B001", "mineral": "Copper", "weight_kg": "1200", "purity_pct": "88.5%"}, # 重复
        {"batch_id": "B004", "mineral": "Aluminum", "weight_kg": "3500", "purity_pct": "78.2%"}, # 不合格
        {"batch_id": "B005", "mineral": "Nickel", "weight_kg": "800", "purity_pct": "86.5"}
    ]
    
    # 简单的混淆编码
    json_str = json.dumps(rfid_data)
    encoded_bytes = base64.b64encode(json_str.encode('utf-8'))
    
    # 加上一点伪造的二进制文件头
    fake_header = b"RFID_SCAN_V2_MAGIC_HEADER_0x8F\n"
    
    with open(dat_file, "wb") as f:
        f.write(fake_header)
        f.write(encoded_bytes)

    # 生成 文本日志 数据 (保持不变，作为交叉验证的来源)
    log_file = "warehouse_reports/manual_notes.txt"
    notes = [
        "BATCH: B006 | MATERIAL: Copper | QTY: 450 | QUALITY: 89.2%",
        "BATCH: B007 | MATERIAL: Zinc | QTY: 1100kg | QUALITY: 84.5", # 不合格
        "BATCH: B008 | MATERIAL: Nickel | QTY: 300 | QUALITY: 92.1%"
    ]
    
    with open(log_file, "w") as f:
        f.write("\n".join(notes))

if __name__ == "__main__":
    build_env()
