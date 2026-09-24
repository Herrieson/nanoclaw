import os
import json
import random

def build_env():
    # 创建目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reference", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 白名单数据
    white_list = ["Maya Angelou", "Gordon Ramsay", "Alice Waters", "James Beard", "Julia Child"]
    with open("reference/white_list.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(white_list))

    # 生成签到记录（包含脏数据和不合规人员）
    log_content = [
        "Date,Name,Check_In,Check_Out",
        "2023-10-23,Maya Angelou,09:00,12:00",  # 3 hours
        "2023-10-23,Unknown Intruder,10:00,11:00", # Intruder
        "2023-10-24,Gordon Ramsay,14:00,17:30", # 3.5 hours
        "2023-10-24,Alice Waters,09:00,11:00",  # 2 hours
        "2023-10-25,Julia Child,13:00,16:00",   # 3 hours
        "2023-10-25,Bad Actor,08:00,09:00",     # Intruder
        "2023-10-26,Maya Angelou,09:00,11:00",  # 2 hours
        "2023-10-26,Gordon Ramsay,14:00,15:00", # 1 hour
    ]
    
    # 模拟分散的文件
    with open("logs/monday_log.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(log_content[:3]))
    
    with open("logs/midweek_log.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log_content[3:6]))
        
    with open("logs/thursday_final.csv", "w", encoding="utf-8") as f:
        f.write("\n".join([log_content[0]] + log_content[6:]))

    # 干扰文件
    with open("logs/grocery_list.txt", "w", encoding="utf-8") as f:
        f.write("Basil, Olive Oil, Garlic, Tomatoes")

if __name__ == "__main__":
    build_env()
