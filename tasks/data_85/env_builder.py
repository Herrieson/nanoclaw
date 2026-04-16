import os
import csv
import json
import base64

def setup_environment():
    base_path = "assets/data_85"
    os.makedirs(base_path, exist_ok=True)

    # 1. 损坏且混乱的 CSV (包含英制单位)
    csv_content = [
        ["sku", "material", "dims_inch", "status", "count"],
        ["OAK-1696", "Red Oak", "1x6x96", "good", "10"],
        ["WAL-2448", "Black Walnut", "2x4x48", "good", "5"],
        ["OAK-1696", "Red Oak", "1x6x96", "damaged", "2"],
        ["PINE-001", "Pine", "2x4x96", "good", "100"]
    ]
    with open(os.path.join(base_path, "legacy_inventory.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_content)

    # 2. 模拟日志文件 (包含公制单位 mm，需要转换: 1 inch = 25.4 mm)
    # 1x6x96 inch 约等于 25.4 x 152.4 x 2438.4 mm
    # 2x4x48 inch 约等于 50.8 x 101.6 x 1219.2 mm
    log_content = [
        "2023-10-01 RECEIVED: Material=Red Oak, Size=25.4x152.4x2438.4mm, Qty=8, Note=New Batch",
        "2023-10-02 RETURNED: Material=Black Walnut, Size=50.8x101.6x1219.2mm, Qty=2, Reason=Warped",
        "2023-10-03 RECEIVED: Material=Black Walnut, Size=50.8x101.6x1219.2mm, Qty=10, Note=A-Grade"
    ]
    with open(os.path.join(base_path, "warehouse_log.txt"), "w") as f:
        f.write("\n".join(log_content))

    # 3. 加密/编码的供应商数据 (Base64 模拟 Marcus 所谓的加密)
    # 增加 5 块橡木，1 块胡桃木
    supplier_data = [
        {"item": "Red Oak", "dim": "1x6x96", "amount": 5, "condition": "verified"},
        {"item": "Black Walnut", "dim": "2x4x48", "amount": 1, "condition": "verified"}
    ]
    encoded_data = base64.b64encode(json.dumps(supplier_data).encode()).decode()
    with open(os.path.join(base_path, "supplier_invoice.json.enc"), "w") as f:
        f.write(encoded_data)

if __name__ == "__main__":
    setup_environment()
