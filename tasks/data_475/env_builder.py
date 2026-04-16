import os
import binascii
import json

def build_env():
    base_path = "assets/data_475"
    os.makedirs(base_path, exist_ok=True)

    # 1. 伪造原始 OBD 二进制日志 (含特定故障码)
    # OBD-II 协议简化模拟: 帧头 + PID + 数据
    # P0171 (System Too Lean Bank 1) 是我们要埋的伏笔
    # 十六进制表示中, 故障码通常在 Mode 03 或特定 Freeze Frame 中
    # 我们构造一个包含 "03 01 71" 序列的二进制文件，混合大量无用数据
    log_content = b"\x00\xFF\xAA" * 100
    log_content += b"\x03\x01\x71" # Target Code P0171
    log_content += b"\xBB\xCC\xDD" * 200
    
    # 模拟测试过程中的时间戳数据块 (含有时间标记)
    # 假设故障发生在 2023-10-27 14:35:22
    timestamp_marker = b"TS:1698417322" 
    log_content = log_content[:500] + timestamp_marker + log_content[500:]

    with open(os.path.join(base_path, "raw_obd_log.bin"), "wb") as f:
        f.write(log_content)

    # 2. 伪造零散的零件订单
    invoices = [
        "Invoice #9921 - Dublin-Jalisco Auto Parts\nItem: Fuel Injector Cleaner\nPrice: $15.50\nStatus: Paid",
        "Invoice #9925 - Dublin-Jalisco Auto Parts\nItem: OEM Fuel Pump\nPrice: $289.99\nStatus: Paid",
        "Note: Bought 4 spark plugs from the shop down the street. $8.00 each. Cash."
    ]
    
    for i, content in enumerate(invoices):
        with open(os.path.join(base_path, f"invoice_00{i}.txt"), "w") as f:
            f.write(content)

    # 3. 伪造一些干扰文件 (体现 Low Conscientiousness)
    with open(os.path.join(base_path, "taco_recipe.txt"), "w") as f:
        f.write("Ingredients for the best Al Pastor... (Personal note, ignore)")
    
    with open(os.path.join(base_path, "car_photos_metadata.json"), "w") as f:
        json.dump({"file": "IMG_001.JPG", "date": "2023-10-27", "notes": "Car looks shiny"}, f)

if __name__ == "__main__":
    build_env()
