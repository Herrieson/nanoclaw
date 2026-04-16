import os
import sqlite3
import random

def build_env():
    base_path = "assets/data_266"
    os.makedirs(base_path, exist_ok=True)

    # 1. 模拟原始损坏的日志文件 (包含非 UTF-8 字符模拟损坏)
    log_path = os.path.join(base_path, "telemetry_raw.log")
    with open(log_path, "wb") as f:
        f.write(b"ID:001,VAL:1500,STATUS:OK\n")
        f.write(b"ID:002,VAL:2300,STATUS:OK\n")
        f.write(b"ID:003,VAL:\xff\xfe\xfd,STATUS:ERROR\n") # 故意制造的损坏字节
        f.write(b"ID:004,VAL:4500,STATUS:OK\n")

    # 2. 模拟有 Bug 的处理脚本
    script_content = """
import os
import sqlite3

def run_processing():
    # 陷阱 1: 缺少环境变量读取逻辑，但脚本依赖它
    db_name = os.getenv("SPACE_DB_NAME", "data_vault.db")
    
    raw_data_path = "telemetry_raw.log"
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS impact (id TEXT, impact_score REAL)")

    try:
        with open(raw_data_path, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                raw_val = parts[1].split(":")[1]
                # 陷阱 2: 这里没有处理非法字符，会报 ValueError
                score = float(raw_val) * 0.85 
                # 陷阱 3: 错误的经济学公式，如果 score > 3000，应当加权 1.2，否则会导致评估偏低
                cursor.execute("INSERT INTO impact VALUES (?, ?)", (parts[0], score))
        conn.commit()
        print("Processing complete.")
    except Exception as e:
        print(f"CRITICAL_FAILURE: {e}")
        exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    run_processing()
"""
    with open(os.path.join(base_path, "processor.py"), "w") as f:
        f.write(script_content)

    # 3. 故意删除环境变量配置，留下一份错误的示例
    with open(os.path.join(base_path, "env_config.sample"), "w") as f:
        f.write("SPACE_DB_NAME=result.db\n# DEBUG_MODE=True")

    # 4. 创建一个只读的 readme，暗示公式
    with open(os.path.join(base_path, "NOTE.txt"), "w") as f:
        f.write("Note from Contractor: The economic impact score must apply a 1.2 multiplier if raw value exceeds 3000. Ensure the DB is named correctly as per Arthur's preference (result.db).")

if __name__ == "__main__":
    build_env()
