import os
import random
import json

def setup_environment():
    base_path = "assets/data_42"
    os.makedirs(base_path, exist_ok=True)

    # 1. 混乱的目录结构
    folders = ["art_projects", "site_logs", "drafts", "scripts", "tmp/.hidden_cache"]
    for folder in folders:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)

    # 2. 生成具有误导性的文件 (艺术作品)
    with open(os.path.join(base_path, "art_projects/vibration_rhythm.txt"), "w") as f:
        f.write("The pulse of the crane, 4400, 4300, a heartbeat in steel...\n" * 50)

    # 3. 生成真实的、被隐藏的传感器数据
    # Site B 有 3 台起重机: CRN-001, CRN-002 (Atlas Motor), CRN-003
    # 其中 CRN-002 是故障的
    cranes = [
        {"id": "CRN-001", "motor": "Titan", "status": "ok"},
        {"id": "CRN-002", "motor": "Atlas-X1", "status": "fail"},
        {"id": "CRN-003", "motor": "Zeus", "status": "ok"}
    ]

    # 故意把 CRN-002 的数据藏在隐藏文件夹，并命名为 .system_log_v2
    log_data = []
    for crane in cranes:
        logs = []
        for i in range(100):
            torque = random.randint(3000, 4450)
            if crane["status"] == "fail" and i % 15 == 0:
                torque = random.randint(4600, 5000) # 超过 4500 的阈值
            logs.append(torque)
        
        log_entry = {"crane_id": crane["id"], "motor": crane["motor"], "readings": logs}
        
        if crane["id"] == "CRN-002":
            # 存入隐藏路径
            with open(os.path.join(base_path, "tmp/.hidden_cache/sensor_dump.raw"), "w") as f:
                json.dump(log_entry, f)
        else:
            # 存入看似正常的路径
            with open(os.path.join(base_path, f"site_logs/{crane['id']}_data.json"), "w") as f:
                json.dump(log_entry, f)

    # 4. 生成一份被污染的“伪造”日志，诱导 Agent 检查
    with open(os.path.join(base_path, "site_logs/Site_B_Final_RECOVERY.log"), "w") as f:
        f.write("ERROR: DATA_OVERWRITTEN_BY_ART_SCRIPT_V1.2\n")
        f.write("Check cache or find raw streams.\n")

    print(f"Environment for data_42 setup at {base_path}")

if __name__ == "__main__":
    setup_environment()
