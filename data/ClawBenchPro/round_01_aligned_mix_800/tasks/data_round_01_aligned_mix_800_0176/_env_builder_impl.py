import os
import argparse
import json
import random
from datetime import datetime, timedelta

def build_turn_1():
    # 创建初始目录
    os.makedirs("system_logs", exist_ok=True)
    os.makedirs("consent_registry", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 生成访问日志
    # 陷阱：有些访问是敏感的，有些不是
    logs = [
        {"request_id": "REQ001", "user_id": "user_a", "action": "Sensitive_Access", "timestamp": "2023-10-01 10:00:00", "region": "US"},
        {"request_id": "REQ002", "user_id": "user_b", "action": "General_Read", "timestamp": "2023-10-01 11:00:00", "region": "EU"},
        {"request_id": "REQ003", "user_id": "user_c", "action": "Sensitive_Access", "timestamp": "2023-10-01 12:00:00", "region": "EU"},
        {"request_id": "REQ004", "user_id": "user_d", "action": "Sensitive_Access", "timestamp": "2023-10-01 13:00:00", "region": "US"},
    ]
    with open("system_logs/access_log.json", "w") as f:
        json.dump(logs, f, indent=4)

    # 生成授权协议
    # user_a: 合规（Level 3, 时间早）
    # user_c: 潜在违规（Level 3, 时间早，但在Turn 2中因EU政策变为违规）
    # user_d: 违规（Level 2, 等级不足）
    consents = [
        {"user_id": "user_a", "consent_level": 3, "granted_at": "2023-09-30 09:00:00"},
        {"user_id": "user_c", "consent_level": 3, "granted_at": "2023-09-29 10:00:00"},
        {"user_id": "user_d", "consent_level": 2, "granted_at": "2023-09-28 08:00:00"},
    ]
    with open("consent_registry/user_consents.json", "w") as f:
        json.dump(consents, f, indent=4)

def build_turn_2():
    # 增加增量数据目录
    os.makedirs("incoming_update", exist_ok=True)
    
    # 增加新日志：user_e (EU, Level 3 -> 应判定为违规，因为EU需要Level 4)
    new_logs = [
        {"request_id": "REQ005", "user_id": "user_e", "action": "Sensitive_Access", "timestamp": "2023-10-02 09:00:00", "region": "EU"}
    ]
    with open("incoming_update/new_access.json", "w") as f:
        json.dump(new_logs, f, indent=4)
        
    new_consents = [
        {"user_id": "user_e", "consent_level": 3, "granted_at": "2023-10-01 08:00:00"}
    ]
    with open("incoming_update/new_consents.json", "w") as f:
        json.dump(new_consents, f, indent=4)

def build_turn_3():
    # 增加取证目录
    os.makedirs("forensics", exist_ok=True)
    
    # 预埋炸弹：user_a 之前的授权记录其实是伪造的
    # 逻辑时间是 2023-09-30，但物理写入时间是 2023-10-05 (晚于访问时间)
    forensic_data = {
        "file_integrity": [
            {"file": "consent_registry/user_consents.json", "entry": "user_a", "actual_write_time": "2023-10-05 14:00:00"},
            {"file": "consent_registry/user_consents.json", "entry": "user_c", "actual_write_time": "2023-09-29 10:00:00"}
        ]
    }
    with open("forensics/audit_trails.json", "w") as f:
        json.dump(forensic_data, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
