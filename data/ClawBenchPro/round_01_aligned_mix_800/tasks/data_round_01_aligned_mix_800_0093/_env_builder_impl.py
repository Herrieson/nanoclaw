import os
import argparse
import csv
import json

def build_turn_1():
    # 创建基础目录
    os.makedirs("pending_shipments", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 车辆状态数据：故意混入多台车，但只有两台是冷链
    fleet_data = [
        ["vehicle_id", "type", "last_maintenance", "status"],
        ["V001", "Dry Van", "2023-10-01", "Active"],
        ["V002", "Reefer", "2023-11-15", "Active"],
        ["V003", "Reefer", "2023-09-20", "Active"],
        ["V004", "Flatbed", "2023-12-01", "Active"],
        ["V005", "Dry Van", "2023-08-05", "Active"]
    ]
    with open("fleet_status.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(fleet_data)

    # 待配送订单：设计陷阱
    # S002 必须冷链，S003 驾驶时长极易超标
    shipments = [
        {"id": "S001", "content": "Electronics", "type": "Dry", "origin": "LA", "dest": "SF", "distance_miles": 380, "priority": "Medium"},
        {"id": "S002", "content": "Vaccines", "type": "Cold", "origin": "LA", "dest": "SD", "distance_miles": 120, "priority": "High"},
        {"id": "S003", "content": "Fresh Seafood", "type": "Cold", "origin": "SF", "dest": "SEA", "distance_miles": 800, "priority": "High"},
        {"id": "S004", "content": "Textiles", "type": "Dry", "origin": "PHX", "dest": "LA", "distance_miles": 370, "priority": "Low"}
    ]
    for s in shipments:
        with open(f"pending_shipments/{s['id']}.json", "w") as f:
            json.dump(s, f)

def build_turn_2():
    os.makedirs("incoming_updates", exist_ok=True)
    
    # 突发状况：V002 坏了 (制冷失效)
    status_update = {
        "incident_report": "V002 refrigeration unit failure at 04:00 AM.",
        "impact": "Can only transport dry goods.",
        "action_required": "Reschedule all assigned cold chain tasks to remaining active reefer."
    }
    with open("incoming_updates/maintenance_alert.json", "w") as f:
        json.dump(status_update, f)
    
    # 新增紧急订单，增加复杂度
    new_shipment = {
        "id": "S005", "content": "Insulin", "type": "Cold", "origin": "LA", "dest": "LV", "distance_miles": 270, "priority": "High"
    }
    with open("incoming_updates/S005.json", "w") as f:
        json.dump(new_shipment, f)

def build_turn_3():
    # 审计模板
    audit_template = {
        "audit_id": "AUDIT-2024-Q1",
        "compliance_checks": [
            {"criterion": "Max Driving Hours", "status": "", "violations": []},
            {"criterion": "Cold Chain Integrity", "status": "", "violations": []}
        ],
        "notes": ""
    }
    with open("audit_template.json", "w") as f:
        json.dump(audit_template, f)

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
