import os
import json
import csv

def build_env():
    # 建立供应商发票目录
    os.makedirs("supplier_invoices", exist_ok=True)
    
    invoice_1 = {
        "vendor": "Green Valley Organics",
        "items": [
            {"product_name": "Organic Avocados", "quantity": 10, "unit_price": 2.50},
            {"product_name": "Artisan Sourdough", "quantity": 5, "unit_price": 8.00}
        ]
    }
    
    invoice_2 = {
        "vendor": "European Imports Ltd",
        "items": [
            {"product_name": "Manchego Cheese (lbs)", "quantity": 20, "unit_price": 15.00},
            {"product_name": "Truffle Oil", "quantity": 12, "unit_price": 25.00}
        ]
    }
    
    invoice_3 = {
        "vendor": "Spice Road Exotics",
        "items": [
            {"product_name": "Heirloom Tomatoes", "quantity": 50, "unit_price": 3.00},
            {"product_name": "Saffron (oz)", "quantity": 1, "unit_price": 80.00}
        ]
    }

    with open("supplier_invoices/inv_001.json", "w") as f:
        json.dump(invoice_1, f, indent=2)
    with open("supplier_invoices/inv_002.json", "w") as f:
        json.dump(invoice_2, f, indent=2)
    with open("supplier_invoices/inv_003.json", "w") as f:
        json.dump(invoice_3, f, indent=2)

    # 建立夜班收货记录目录 (带有脏数据)
    os.makedirs("shift_logs", exist_ok=True)
    
    # 真实情况:
    # Organic Avocados: 收了 8 个 (少了 2 个) -> 2 * 2.50 = 5.00
    # Artisan Sourdough: 收了 5 个 (正常)
    # Manchego Cheese (lbs): 收了 20 个 (正常)
    # Truffle Oil: 收了 10 个 (少了 2 个) -> 2 * 25.00 = 50.00
    # Heirloom Tomatoes: 收了 55 个 (多了 5 个，User只关心少了的被坑的钱，多的不用算)
    # Saffron (oz): 收了 0 个 (少了 1 个) -> 1 * 80.00 = 80.00
    # 丢失总金额 = 5.00 + 50.00 + 80.00 = 135.00
    
    received_data = [
        ["Item Scanned", "Qty"],
        ["  organic Avocados", "8"],
        ["artisan sourdough ", "5"],
        [" Manchego Cheese (LBS)", "20"],
        ["truffle oil", "10"],
        ["Heirloom Tomatoes  ", "55"]
        # Saffron 完全没有被记录 (直接漏掉)
    ]

    with open("shift_logs/receiving_night_shift.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(received_data)

if __name__ == "__main__":
    build_env()
