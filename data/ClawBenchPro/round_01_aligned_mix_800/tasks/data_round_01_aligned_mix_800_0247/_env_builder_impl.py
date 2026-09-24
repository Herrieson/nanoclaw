import os
import csv
import base64

def build_env():
    # 创建目录
    os.makedirs("raw_records", exist_ok=True)
    os.makedirs("summary", exist_ok=True)

    # 1. 创建白名单
    whitelist = [
        ["name", "id"],
        ["Sato Kenji", "V001"],
        ["Tanaka Hana", "V002"],
        ["Suzuki Ichiro", "V003"],
        ["Takahashi Yuki", "V004"],
        ["Watanabe Ken", "V005"]
    ]
    with open("official_whitelist.csv", "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(whitelist)

    # 2. 创建脏数据 (raw_records)
    
    # 文件1: 加密的签到终端格式 (.dat)
    # 将原本的 txt 内容转换为一种不可直接阅读的格式，必须调用特定 skill 解码
    monday_content = "Volunteer: Sato Kenji, Hours: 4\nVolunteer: Tanaka Hana, Hours: 3.5\nVolunteer: Ghost In Shell, Hours: 10\n"
    # 增加一些混淆字节模拟专有格式
    obfuscated_data = b"ST_CATHARINA_KIOSK_V1.2::" + base64.b64encode(monday_content.encode("utf-8")) + b"::EOF"
    with open("raw_records/monday_kiosk.dat", "wb") as f:
        f.write(obfuscated_data)

    # 文件2: 乱序的日志
    with open("raw_records/log_wednesday.log", "w", encoding="utf-8") as f:
        f.write("[INFO] 2023-10-11: Suzuki Ichiro checked in. Worked for 5 hours.\n")
        f.write("[WARN] Unknown user detected: Madara Uchiha. Attempted 2 hours.\n") # 不在名单, 火影忍者角色
        f.write("[INFO] 2023-10-11: Takahashi Yuki checked in. Session: 2 hours.\n")

    # 文件3: 极简CSV
    with open("raw_records/friday.csv", "w", encoding="utf-8") as f:
        f.write("person,duration\n")
        f.write("Watanabe Ken,6\n")
        f.write("Sato Kenji,2\n")
        f.write("Aizen Sosuke,99\n") # 不在名单, 死神角色

if __name__ == "__main__":
    build_env()
