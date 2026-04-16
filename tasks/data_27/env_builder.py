import os
import sqlite3
import json
import xml.etree.ElementTree as ET

def setup_environment():
    base_dir = "assets/data_27"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "backups"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "logs"), exist_ok=True)

    # 1. 创建一个损坏的 SQLite 数据库 (模拟二进制损坏)
    db_path = os.path.join(base_dir, "human_resource_v4.db")
    with open(db_path, "wb") as f:
        f.write(b"SQLITE3\0...CORRUPTED_DATA..." * 100)

    # 2. 生成碎片化的备份数据 (XML 格式)
    # 员工 A (符合条件)
    root = ET.Element("Employees")
    emp1 = ET.SubElement(root, "Employee")
    ET.SubElement(emp1, "Name").text = "micheal o'donnell"
    ET.SubElement(emp1, "Status").text = "Terminated"
    ET.SubElement(emp1, "Plan").text = "PPO"
    ET.SubElement(emp1, "SSN").text = "123-45-678"
    
    # 员工 B (不符合条件: 计划不对)
    emp2 = ET.SubElement(root, "Employee")
    ET.SubElement(emp2, "Name").text = "Sarah Jenkins"
    ET.SubElement(emp2, "Status").text = "Terminated"
    ET.SubElement(emp2, "Plan").text = "HMO"
    ET.SubElement(emp2, "SSN").text = "234-56-789"

    tree = ET.ElementTree(root)
    tree.write(os.path.join(base_dir, "backups/export_part1.xml"))

    # 3. 在日志中隐藏关键信息 (纯文本解析)
    log_content = """
    2023-10-24 09:15:22 - INFO - User logged in: Administrator
    2023-10-24 10:05:01 - ERROR - System Crash detected during entry for employee: Bridget Murphy. 
    Status: Terminated, Plan: PPO, SSN: 345-67-890. Eligibility: Confirmed.
    2023-10-24 10:06:12 - WARNING - Database human_resource_v4.db integrity check failed.
    """
    with open(os.path.join(base_dir, "logs/system_event.log"), "w") as f:
        f.write(log_content)

    # 4. 生成另一份碎片备份 (JSON 格式)
    other_data = [
        {"name": "Robert Smith", "status": "Active", "plan": "PPO", "ssn": "456-78-901"},
        {"name": "Eileen Walsh", "status": "Terminated", "plan": "PPO", "ssn": "567-89-012"}
    ]
    with open(os.path.join(base_dir, "backups/temp_cache.json"), "w") as f:
        json.dump(other_data, f)

if __name__ == "__main__":
    setup_environment()
