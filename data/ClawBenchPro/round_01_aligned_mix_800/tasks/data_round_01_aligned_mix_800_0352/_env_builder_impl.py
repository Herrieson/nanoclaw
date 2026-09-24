import os
import json
import binascii

def build_env():
    # 创建目录结构
    os.makedirs("invoices", exist_ok=True)
    os.makedirs("final_audit", exist_ok=True)

    # 1. 生成发票数据 (invoices)
    # 包含干扰项：非合规的供应商
    invoices = [
        {"id": "INV-001", "supplier": "Redwood Supplies", "item": "2x4 Pine Studs", "amount": 1200, "status": "pending"},
        {"id": "INV-002", "supplier": "Oak & Iron", "item": "Hardwood Flooring", "amount": 4500, "status": "pending"},
        {"id": "INV-003", "supplier": "Cheap Junk Wood Co.", "item": "Plywood Scrap", "amount": 300, "status": "pending"}, # 非法
        {"id": "INV-004", "supplier": "Bay Area Lumber", "item": "Cedar Planks", "amount": 2100, "status": "pending"},
        {"id": "INV-005", "supplier": "Unknown Scraps", "item": "Sawdust", "amount": 50, "status": "pending"}, # 非法
    ]
    
    for inv in invoices:
        with open(f"invoices/{inv['id']}.json", "w") as f:
            json.dump(inv, f)

    # 2. 生成现场签收记录并进行十六进制编码 (模拟 RFID 二进制 Dump)
    # 原始 CSV 内容：
    # timestamp,invoice_id,condition
    # 2023-10-01 08:00,INV-001,Good
    # 2023-10-01 10:30,INV-002,Damaged edge
    # 2023-10-02 09:15,INV-003,Poor
    # 2023-10-02 14:00,INV-005,N/A
    # 注意：INV-004 还没到货，INV-003 虽然是非法的但居然被签收了
    csv_content = (
        "timestamp,invoice_id,condition\n"
        "2023-10-01 08:00,INV-001,Good\n"
        "2023-10-01 10:30,INV-002,Damaged edge\n"
        "2023-10-02 09:15,INV-003,Poor\n"
        "2023-10-02 14:00,INV-005,N/A\n"
    )
    rfid_hex = binascii.hexlify(csv_content.encode('utf-8')).decode('utf-8')
    
    with open("site_log.rfid", "w") as f:
        f.write(rfid_hex)

    # 3. 干扰文件：一些无关的木工草图
    with open("sketch.txt", "w") as f:
        f.write("Stairs: 7.5 inch rise, 10 inch run. Don't forget the multi-tool.\nAlso, IT mentioned the old NCSR SOAP API is dead.")

if __name__ == "__main__":
    build_env()
