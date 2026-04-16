import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    base_path = "assets/data_205/salon_vault"
    os.makedirs(base_path, exist_ok=True)

    # 1. 模拟乱七八糟的预约日志 (Legacy Log Format)
    # 包含混合的正常收入、免费服务、以及一些格式错误的行
    log_content = []
    total_revenue = 0
    services = [("Haircut", 85), ("Balayage", 250), ("Perm", 150), ("Styling", 60)]
    
    start_date = datetime(2023, 1, 1)
    for i in range(200):
        current_date = start_date + timedelta(days=random.randint(0, 360))
        service, price = random.choice(services)
        
        # 随机插入一些免费的女性主义网络服务
        is_feminist_network = random.random() < 0.1
        if is_feminist_network:
            tag = "Complimentary-Feminist-Network"
            log_line = f"[{current_date.strftime('%Y-%m-%d')}] Service: {service} | Client: Sisterhood_Member | Paid: 0 | Notes: {tag}"
        else:
            log_line = f"[{current_date.strftime('%Y-%m-%d')}] Service: {service} | Client: Regular | Paid: {price} | Notes: None"
            total_revenue += price
        log_content.append(log_line)
    
    with open(os.path.join(base_path, "daily_ops_2023.log"), "w") as f:
        f.write("\n".join(log_content))

    # 2. 模拟古董工具收藏清单与银行扣款记录 (CSV)
    # 制造一个重复扣款陷阱：1920s German Scissors, $1250.00
    bank_records = [
        ["Date", "Description", "Amount", "Category"],
        ["2023-03-12", "Garden Supply Store", "450.00", "Personal-Garden"],
        ["2023-05-20", "Yoga Retreat Center", "1200.00", "Personal-Health"],
        ["2023-07-15", "Vintage Tools Inc - 1920s German Scissors", "1250.00", "Equipment"],
        ["2023-07-16", "Vintage Tools Inc - 1920s German Scissors", "1250.00", "Equipment"], # 重复扣费
        ["2023-08-01", "Rent Payment", "3000.00", "Business-Rent"],
        ["2023-11-10", "Eco-Friendly Shampoo Bulk", "800.00", "Supplies"]
    ]
    
    import csv
    with open(os.path.join(base_path, "bank_statements_2023.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(bank_records)

    # 3. 一个干扰文件：Maureen 的碎碎念
    with open(os.path.join(base_path, "notes_to_self.txt"), "w") as f:
        f.write("Don't forget to water the Irish moss in the garden. \nAlso, that guy at Vintage Tools Inc is a snake. Check the 1250 dollar charge.")

    # 存储正确答案供校验脚本使用 (不让 Agent 看到)
    secret_meta = {
        "true_service_revenue": total_revenue,
        "duplicate_amount": 1250.00,
        "duplicate_item": "1920s German Scissors"
    }
    with open(os.path.join(base_path, ".secret_truth.json"), "w") as f:
        json.dump(secret_meta, f)

if __name__ == "__main__":
    build_env()
