import os
import csv

def build_env():
    # 创建目录结构
    os.makedirs("records/invoices", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. 生成 CSV 格式的进货单 - 移除了明文标签，引入 ID
    # 供应商关系：
    # V-9901: Organic Apples (Exp 2023-12-20) -> 过期
    # V-1102: Local Honey (Exp 2024-06-01) -> 合格 (Certified, Gold)
    # V-4403: Soda (Exp 2024-11-10) -> 不合格 (Non-Organic)
    csv_data = [
        ["sku", "item_name", "vendor_id", "delivery_date", "expiry_date", "unit_price", "quantity"],
        ["SKU-001", "Organic Apples", "V-9901", "2023-11-01", "2023-12-20", "1.5", "100"],
        ["SKU-002", "Local Honey", "V-1102", "2023-11-05", "2024-06-01", "12.0", "10"],
        ["SKU-003", "Plastic Bottled Soda", "V-4403", "2023-11-10", "2024-11-10", "0.5", "200"]
    ]
    with open("records/invoices/batch_01.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # 2. 生成 PDF 占位文件 (暗示需要 OCR)
    # 内容逻辑：
    # Sustainable Oats (SKU-005, Vendor V-2201), Exp 2024-08-20, Price 3.5, Qty 20 -> 合格 (Certified, Silver)
    # Organic Berries (SKU-006, Vendor V-1102), Exp 2023-12-28, Price 4.0, Qty 15 -> 过期
    with open("records/invoices/batch_02.pdf", "w") as f:
        f.write("%PDF-1.4 [Binary Data - Image of Invoice]\n")
        f.write("Invoice_ID: INV-2023-009\nItems: Sustainable Oats, Organic Berries\n")

    # 3. 干扰项
    with open("bird_calls_notes.txt", "w") as f:
        f.write("Today I heard a Northern Flicker. Its call is a loud, rhythmic 'wick-wick-wick'.")

if __name__ == "__main__":
    build_env()
