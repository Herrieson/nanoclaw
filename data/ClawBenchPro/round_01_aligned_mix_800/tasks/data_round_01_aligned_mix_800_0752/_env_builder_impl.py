import os
import csv
import json

def build_env():
    # 创建目录结构
    os.makedirs("invoices", exist_ok=True)
    os.makedirs("final_audit", exist_ok=True)

    # 1. 白名单供应商
    approved_suppliers = ["Redwood Supplies", "Oak & Iron", "Bay Area Lumber"]
    with open("approved_suppliers.json", "w") as f:
        json.dump({"approved": approved_suppliers}, f)

    # 2. 生成发票数据 (invoices)
    # 包含干扰项：不在白名单的供应商
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

    # 3. 生成现场签收记录 (site_log.csv)
    # 注意：INV-004 还没到货，INV-003 虽然是非法的但居然被签收了（干扰逻辑）
    site_log = [
        ["timestamp", "invoice_id", "condition"],
        ["2023-10-01 08:00", "INV-001", "Good"],
        ["2023-10-01 10:30", "INV-002", "Damaged edge"],
        ["2023-10-02 09:15", "INV-003", "Poor"],
        ["2023-10-02 14:00", "INV-005", "N/A"]
    ]
    
    with open("site_log.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(site_log)

    # 干扰文件：一些无关的木工草图
    with open("sketch.txt", "w") as f:
        f.write("Stairs: 7.5 inch rise, 10 inch run. Don't forget the multi-tool.")

if __name__ == "__main__":
    build_env()
