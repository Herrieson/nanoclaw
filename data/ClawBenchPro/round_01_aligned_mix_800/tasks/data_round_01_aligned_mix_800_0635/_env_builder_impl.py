import os
import json
import csv

def build_env():
    # 创建目录结构
    os.makedirs("records/invoices", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. 生成 CSV 格式的进货单
    csv_data = [
        ["item_name", "category", "delivery_date", "expiry_date", "unit_price", "quantity", "tags"],
        ["Organic Apples", "Fruit", "2023-11-01", "2023-12-20", "1.5", "100", "Organic"],
        ["Local Honey", "Sweetener", "2023-11-05", "2024-06-01", "12.0", "10", "Sustainable"],
        ["Plastic Bottled Soda", "Drink", "2023-11-10", "2024-11-10", "0.5", "200", "Industrial"],
        ["Organic Kale", "Vegetable", "2023-11-15", "2023-12-25", "2.0", "50", "Organic"],
        ["Free-range Eggs", "Dairy", "2023-12-01", "2024-01-15", "5.0", "30", "Sustainable"]
    ]
    with open("records/invoices/batch_01.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # 2. 生成 JSON 格式的进货单 (包含干扰项和脏数据)
    json_data = [
        {
            "product": "Sustainable Oats",
            "type": "Grain",
            "dates": {"delivery": "2023-11-20", "expiry": "2024-08-20"},
            "cost_per_unit": 3.5,
            "amount": 20,
            "labels": ["Sustainable"]
        },
        {
            "product": "Industrial White Sugar",
            "type": "Sweetener",
            "dates": {"delivery": "2023-11-20", "expiry": "2025-01-01"},
            "cost_per_unit": 1.0,
            "amount": 50,
            "labels": ["Cheap"]
        },
        {
            "product": "Organic Berries",
            "type": "Fruit",
            "dates": {"delivery": "2023-12-10", "expiry": "2023-12-28"},
            "cost_per_unit": 4.0,
            "amount": 15,
            "labels": ["Organic"]
        }
    ]
    with open("records/invoices/batch_02.json", "w") as f:
        json.dump(json_data, f)

    # 3. 增加一个无关的背景文件 (干扰项)
    with open("bird_calls_notes.txt", "w") as f:
        f.write("Today I heard a Northern Flicker. Its call is a loud, rhythmic 'wick-wick-wick'.")

if __name__ == "__main__":
    build_env()
