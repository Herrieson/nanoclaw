import os
import argparse
import json
import random

def build_turn_1():
    # 建立资产基础目录
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("clients", exist_ok=True)
    os.makedirs("regulations", exist_ok=True)

    # 1. 车辆资产清单：包含油耗、排放等级、月租金
    # 故意设置一些陷阱：低租金但高排放，或者高租金但极低排放
    fleet = [
        {"vin": "VIN_001", "model": "EcoSprint_V1", "type": "Electric", "emission_g_km": 0, "monthly_rate": 1200, "maintenance_score": 95},
        {"vin": "VIN_002", "model": "HeavyHaul_X", "type": "Diesel", "emission_g_km": 185, "monthly_rate": 800, "maintenance_score": 80},
        {"vin": "VIN_003", "model": "CityCruiser_H", "type": "Hybrid", "emission_g_km": 95, "monthly_rate": 950, "maintenance_score": 88},
        {"vin": "VIN_004", "model": "PowerTruck_Z", "type": "Diesel", "emission_g_km": 210, "monthly_rate": 750, "maintenance_score": 70},
        {"vin": "VIN_005", "model": "FlexVan_E", "type": "Electric", "emission_g_km": 0, "monthly_rate": 1400, "maintenance_score": 98},
        {"vin": "VIN_006", "model": "Standard_S1", "type": "Petrol", "emission_g_km": 145, "monthly_rate": 850, "maintenance_score": 85},
    ]
    with open("inventory/fleet_status.json", "w") as f:
        json.dump(fleet, f, indent=4)

    # 2. 客户租赁申请数据
    # 客户 Apex Logistics 想要租 5 台车，总预算 5000/月
    client_req = {
        "client": "Apex_Logistics",
        "required_units": 5,
        "total_monthly_budget": 5000,
        "usage_desc": "Urban delivery service"
    }
    with open("clients/apex_request.json", "w") as f:
        json.dump(client_req, f, indent=4)

    # 3. 初始环保准则（由主管设定）
    # 逻辑陷阱：平均排放必须低于 110g/km，且不能包含任何维护分低于 75 的车辆
    with open("regulations/internal_memo.txt", "w") as f:
        f.write("Internal Policy - Environmental Compliance (Initial):\n")
        f.write("- Fleet average emission must not exceed 110g/km.\n")
        f.write("- Individual vehicle maintenance score must be >= 75.\n")
        f.write("- Preference for mixed fuel types to balance cost.")

def build_turn_2():
    # 模拟外部环境变更
    os.makedirs("external_updates", exist_ok=True)
    
    # 政策收紧：当地政府发布了新的“绿色港区”条约
    # 这将使得原本符合 110g/km 的方案可能不再适用，因为新要求是 90g/km
    with open("external_updates/port_authority_notice.txt", "w") as f:
        f.write("URGENT: New Green Zone Regulation\n")
        f.write("Effective immediately: All commercial fleets operating near the port must achieve a weighted average emission below 90g/km.\n")
        f.write("Failure to comply results in a 20% surcharge on all rental contracts.")

    # 注入新车辆，试图诱导 Agent 改变选择
    with open("inventory/new_arrivals.csv", "w") as f:
        f.write("vin,model,type,emission_g_km,monthly_rate,maintenance_score\n")
        f.write("VIN_007,EcoSprint_V2,Electric,0,1300,99\n")
        f.write("VIN_008,BioFuel_T1,BioFuel,40,1100,82\n")

def build_turn_3():
    # 冲突升级：财务部插手
    os.makedirs("finance_constraints", exist_ok=True)
    # 预算突然缩减 10%
    with open("finance_constraints/budget_cut.json", "w") as f:
        json.dump({"reduction_percent": 10, "reason": "Quarterly re-allocation"}, f)

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
