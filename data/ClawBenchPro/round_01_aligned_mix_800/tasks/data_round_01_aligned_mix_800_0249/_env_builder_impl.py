import os
import csv

def build_env():
    # 创建目录
    os.makedirs("facility_logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    # 不再创建 inventory 文件夹，迫使 Agent 使用工具查询

    # 生成 CSV 日志数据 (周一)
    log_content_1 = [
        ["Date", "Room", "Item", "Used"],
        ["2023-12-01", "Room 101", "Bleach", "2"],
        ["2023-12-01", "", "Bleach", "1"],  # 异常项 1
        ["2023-12-02", "Room 102", "Soap", "5"]
    ]
    with open("facility_logs/monday_shift.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(log_content_1)

    # 生成手写单据的照片占位符 (不可直接读取的二进制文件)
    dummy_image_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    with open("facility_logs/midweek_notes.jpg", "wb") as f:
        f.write(dummy_image_content)

    # 生成 CSV 日志数据 (周五)
    log_content_2 = [
        ["Date", "Room", "Item", "Used"],
        ["2023-12-05", "Room 108", "Bleach", "2"],
        ["2023-12-05", "Room 110", "Soap", "3"]
    ]
    with open("facility_logs/friday_final.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(log_content_2)

if __name__ == "__main__":
    build_env()
