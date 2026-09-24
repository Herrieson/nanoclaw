import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # 创建目录结构
    os.makedirs("sys_config/clearance", exist_ok=True)
    os.makedirs("raw_telemetry/terminal_alpha", exist_ok=True)
    os.makedirs("raw_telemetry/terminal_beta", exist_ok=True)
    os.makedirs("raw_telemetry/terminal_gamma", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 构建白名单系统
    first_names = ["Maya", "Gordon", "Alice", "James", "Julia", "Anthony", "Nigella", "Jamie", "Massimo", "Rene"]
    last_names = ["Angelou", "Ramsay", "Waters", "Beard", "Child", "Bourdain", "Lawson", "Oliver", "Bottura", "Redzepi"]
    
    volunteers = []
    for i in range(50):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        if name not in [v['name'] for v in volunteers]:
            # 随机分配状态和过期时间
            status = random.choice(["active", "inactive", "suspended"])
            year = random.choice([2022, 2023, 2024])
            month = random.randint(1, 12)
            cert_expiry = f"{year}-{month:02d}-15"
            volunteers.append({"id": f"VOL_{i:03d}", "name": name, "status": status, "cert_expiry": cert_expiry})

    # 写入 clearance 碎片
    for v in volunteers:
        # 添加一些噪音字段
        data = v.copy()
        data["blood_type"] = random.choice(["A", "B", "O", "AB"])
        data["favorite_spice"] = random.choice(["Basil", "Cumin", "Paprika", "Saffron"])
        with open(f"sys_config/clearance/{v['id']}_profile.json", "w", encoding="utf-8") as f:
            json.dump(data, f)
            
    # 添加干扰文件在 clearance 目录下
    for i in range(10):
        with open(f"sys_config/clearance/tmp_cache_{i}.bak", "w", encoding="utf-8") as f:
            f.write("ERR: MEMORY LEAK\n" * 10)

    # 确定真正的白名单人员
    valid_names = set()
    for v in volunteers:
        if v["status"] == "active" and v["cert_expiry"] >= "2023-10-01":
            valid_names.add(v["name"])

    # 2. 构建日志系统
    terminals = ["terminal_alpha", "terminal_beta", "terminal_gamma"]
    intruders = ["Sneaky Pete", "Hungry Hobo", "Unknown Intruder", "Rival Chef"]
    it_testers = ["Admin", "TestUser"]
    
    start_date = datetime(2023, 10, 1)
    
    for day in range(30):
        current_date = start_date + timedelta(days=day)
        date_str = current_date.strftime("%Y-%m-%d")
        
        for term in terminals:
            # 每天每个终端生成一份日志
            log_lines = []
            log_lines.append("SESSION_START")
            log_lines.append("TIME_IN|TIME_OUT|NAME|DEVICE_STATUS")
            
            # 生成 5-15 条打卡记录
            for _ in range(random.randint(5, 15)):
                # 决定人员类型 (80% 合法人员，10% 入侵者，10% IT测试)
                r = random.random()
                if r < 0.8:
                    person = random.choice(volunteers)["name"]
                elif r < 0.9:
                    person = random.choice(intruders)
                else:
                    person = random.choice(it_testers)
                
                # 生成打卡时间
                hour_in = random.randint(8, 14)
                minute_in = random.randint(0, 59)
                duration = random.uniform(1.0, 4.5)
                time_in_dt = current_date.replace(hour=hour_in, minute=minute_in)
                time_out_dt = time_in_dt + timedelta(hours=duration)
                
                time_in_str = time_in_dt.strftime("%Y-%m-%d %H:%M:%S")
                time_out_str = time_out_dt.strftime("%Y-%m-%d %H:%M:%S")
                
                # 写入行
                log_lines.append(f"{time_in_str}|{time_out_str}|{person}|OK")
                
                # 随机加入一点坏行（如传感器异常）
                if random.random() < 0.05:
                    log_lines.append(f"{time_in_str}|ERR_MISSING_OUT|{person}|SENSOR_FAIL")
                if random.random() < 0.02:
                    log_lines.append("?????||||GARBAGE_DATA_*&^%$")

            log_lines.append("SESSION_END")
            
            # 写入日志文件
            filename = f"raw_telemetry/{term}/log_{date_str}.log"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines))

if __name__ == "__main__":
    build_env()
