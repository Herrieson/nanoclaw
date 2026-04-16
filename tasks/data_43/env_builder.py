import os
import json
import pandas as pd
import random

def setup_environment():
    base_dir = "assets/data_43"
    os.makedirs(base_dir, exist_ok=True)

    # 1. 创建 Legacy Inventory CSV (真值)
    legacy_data = [
        {"SKU": "MH-001", "Name": "Missouri Silk Scarf", "Unit_Price": 85.0, "Category": "Apparel"},
        {"SKU": "MH-002", "Name": "Heritage Denim Jacket", "Unit_Price": 120.0, "Category": "Apparel"},
        {"SKU": "MH-003", "Name": "Classic Work Boots", "Unit_Price": 150.0, "Category": "Footwear"},
        {"SKU": "MH-004", "Name": "Embroidered Cotton Shirt", "Unit_Price": 65.0, "Category": "Apparel"},
        {"SKU": "MH-005", "Name": "Leather Belt", "Unit_Price": 45.0, "Category": "Accessories"},
        {"SKU": "MH-006", "Name": "Vintage Wool Hat", "Unit_Price": 55.0, "Category": "Apparel"}
    ]
    pd.DataFrame(legacy_data).to_csv(os.path.join(base_dir, "legacy_inventory.csv"), index=False)

    # 2. 创建 Cloud Export JSON (带错误的待修复数据)
    cloud_data = [
        {"SKU": "MH-001", "Name": "Missouri Silk Scarf", "Unit_Price": 45.0, "On_Hand": 20, "Category": "Apparel"}, # 价格错
        {"SKU": "MH-002", "Name": "Heritage Denim Jacket", "Unit_Price": 120.0, "On_Hand": -15, "Category": "Apparel"}, # 库存负
        {"SKU": "MH-003", "Name": "Classic Work Boots", "Unit_Price": 150.0, "On_Hand": 60, "Category": "Footwear"},
        {"SKU": "MH-004", "Name": "Embroidered Cotton Shirt", "Unit_Price": 30.0, "On_Hand": 10, "Category": "Apparel"}, # 价格错
        {"SKU": "MH-005", "Name": "Leather Belt", "Unit_Price": 45.0, "On_Hand": 100, "Category": "Accessories"},
        {"SKU": "MH-006", "Name": "Vintage Wool Hat", "Unit_Price": 55.0, "On_Hand": -5, "Category": "Apparel"} # 库存负
    ]
    with open(os.path.join(base_dir, "cloud_export.json"), "w") as f:
        json.dump(cloud_data, f, indent=4)

    # 3. 创建系统日志 System Logs
    logs = [
        "2023-10-27 08:00:01 - INFO - System migration started.",
        "2023-10-27 08:15:22 - ERROR - Variance detected for SKU MH-002. Inventory Adjusted: +40",
        "2023-10-27 08:15:45 - ERROR - Variance detected for SKU MH-006. Inventory Adjusted: +15",
        "2023-10-27 09:00:00 - INFO - Migration completed with warnings."
    ]
    with open(os.path.join(base_dir, "system_logs.log"), "w") as f:
        f.write("\n".join(logs))

if __name__ == "__main__":
    setup_environment()
