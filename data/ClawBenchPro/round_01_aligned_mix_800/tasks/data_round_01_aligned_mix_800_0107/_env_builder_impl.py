import os
import argparse
import random
import json

def build_turn_1():
    # 供应商原始数据：包含报价、载客量、排放等级、历史投诉
    # 路径已由框架设定为 assets/data_round_01_aligned_mix_800_0107/turn_1
    os.makedirs("vendor_data", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)
    
    vendors = [
        {"id": "V-001", "name": "BlueRidge Shuttle", "daily_rate": 450, "capacity": 15, "emission_tier": "Euro 4", "complaints": 2},
        {"id": "V-002", "name": "EcoHike Logistics", "daily_rate": 580, "capacity": 12, "emission_tier": "Zero Emission", "complaints": 0},
        {"id": "V-003", "name": "Summit Explorer", "daily_rate": 390, "capacity": 20, "emission_tier": "Euro 5", "complaints": 5}, # 投诉高
        {"id": "V-004", "name": "Valley View Bus", "daily_rate": 500, "capacity": 18, "emission_tier": "Euro 6", "complaints": 1},
        {"id": "V-005", "name": "Retro Trails", "daily_rate": 300, "capacity": 10, "emission_tier": "Euro 3", "complaints": 0}, # 排放差
    ]
    with open("vendor_data/vendors.json", "w") as f:
        json.dump(vendors, f, indent=4)

    # 路线日志数据：包含起始点、预计时长、路段限制
    routes = [
        {"route_id": "R1", "name": "Old Oak Trail", "length_km": 12, "max_capacity": 50, "protected_zone": False},
        {"route_id": "R2", "name": "Eagle Peak Path", "length_km": 8, "max_capacity": 25, "protected_zone": True},
        {"route_id": "R3", "name": "River Run Loop", "length_km": 15, "max_capacity": 60, "protected_zone": False},
    ]
    with open("vendor_data/routes.json", "w") as f:
        json.dump(routes, f, indent=4)

    # 初始预订请求
    bookings = [
        {"booking_id": "B-101", "tourist_count": 14, "route": "R2", "date": "2023-11-01"},
        {"booking_id": "B-102", "tourist_count": 25, "route": "R1", "date": "2023-11-01"},
        {"booking_id": "B-103", "tourist_count": 8, "route": "R3", "date": "2023-11-02"},
    ]
    with open("raw_logs/pending_bookings.json", "w") as f:
        json.dump(bookings, f, indent=4)

def build_turn_2():
    # 模拟环境变化：新增突发紧急封锁通知和新环保红线
    os.makedirs("notifications", exist_ok=True)
    
    # 冲突点：Eagle Peak Path (R2) 突然因为降雨封锁
    # 冲突点：环保局新通知，所有进入 protected_zone 的车辆必须是 Zero Emission
    with open("notifications/urgent_alert.txt", "w") as f:
        f.write("ALERT: R2 (Eagle Peak Path) is closed due to landslide risk from 2023-11-01 to 2023-11-05.\n")
        f.write("NEW POLICY: Effective immediately, any route marked as 'protected_zone' strictly prohibits non-Zero-Emission vehicles.")

    # 新增一批游客，必须处理
    new_bookings = [
        {"booking_id": "B-104", "tourist_count": 10, "route": "R1", "date": "2023-11-01"}
    ]
    with open("raw_logs/new_bookings.json", "w") as f:
        json.dump(new_bookings, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
