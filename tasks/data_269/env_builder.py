import os
import base64
import random
from datetime import datetime, timedelta

def setup_environment():
    base_path = "assets/data_269"
    raw_data_path = os.path.join(base_path, "raw_data")
    os.makedirs(raw_data_path, exist_ok=True)

    # 1. 生成损坏的 CSV 数据 (Batch-X74)
    csv_content = "id,batch_id,drug_name,unit_price_enc\n"
    target_batch = "Batch-X74"
    other_batches = ["Batch-A12", "Batch-B88"]
    
    # 正确的数据（需要被提取）
    prices = [45.50, 120.00, 89.99, 210.50]
    for i, price in enumerate(prices):
        # 故意加上干扰字符的 Base64
        b64_price = base64.b64encode(str(price).encode()).decode() + "==IGNORE=="
        csv_content += f"{i+1},{target_batch},Drug_{i},{b64_price}\n"
    
    # 干扰数据
    for i in range(5, 10):
        csv_content += f"{i},Batch-A12,Old_Drug_{i},MTIzLjQ1\n"

    with open(os.path.join(raw_data_path, "inventory.csv"), "w") as f:
        f.write(csv_content)

    # 2. 生成带偏移的时间监控日志 (temp_logs.txt)
    # 假设当前时间是 2023-10-27 10:00:00
    # 实际发生异常的时间是 12:05:00，但日志显示 14:05:00 (偏移了7200秒)
    log_path = os.path.join(base_path, "temp_logs.txt")
    start_time = datetime(2023, 10, 27, 12, 0, 0) # 实际开始
    
    logs = []
    for i in range(20):
        current_actual_time = start_time + timedelta(minutes=i*5)
        # 加上 7200 秒偏移
        logged_time = current_actual_time + timedelta(seconds=7200)
        
        # 制造异常：在第 12:05 和 12:10 的时候温度过高 (8.5 and 9.1)
        temp = 4.0 + random.uniform(0, 1.0)
        if i == 1 or i == 2:
            temp = 8.5 if i == 1 else 9.1
            
        logs.append(f"[{logged_time.strftime('%Y-%m-%d %H:%M:%S')}] TEMP: {temp:.2f}C STATUS: OK")

    with open(log_path, "w") as f:
        f.write("\n".join(logs))

if __name__ == "__main__":
    setup_environment()
