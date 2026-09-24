import os
import argparse
import random
import json

def build_turn_1():
    # 初始环境：混乱的资产文件夹和损坏的日志
    os.makedirs("field_reports/node_alpha", exist_ok=True)
    os.makedirs("specs", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)
    
    # 节点 A 的设备日志，包含干扰项
    with open("field_reports/node_alpha/equipment_logs.txt", "w") as f:
        f.write("TIMESTAMP: 2023-10-01 08:00 | DEV_ID: OLT-X1 | STATUS: OPERATIONAL\n")
        f.write("TIMESTAMP: 2023-10-01 10:45 | DEV_ID: SPLITTER-09 | ERR: ATTENUATION_HIGH (15dB)\n")
        f.write("TIMESTAMP: 2023-10-01 11:30 | DEV_ID: OLT-X1 | WARN: TEMPERATURE_THRESHOLD_90C\n")
        f.write("TIMESTAMP: 2023-10-02 02:15 | DEV_ID: TRANSCEIVER-A2 | STATUS: FAILED\n")
        f.write("TIMESTAMP: 2023-10-02 09:00 | DEV_ID: SPLITTER-09 | ERR: CRITICAL_SIGNAL_LOSS\n")

    # 设备规格说明书 (非结构化)
    with open("specs/standard_ops.md", "w") as f:
        f.write("# Fiber Infrastructure Standard Ops\n\n")
        f.write("Maximum allowable attenuation for Tier-1 splitters is 12dB. Anything higher requires immediate replacement.\n")
        f.write("OLT units must operate below 85C. If logs show >90C, cooling fan sub-units (CF-Series) must be retrofitted.\n")
        f.write("Critical signal loss in passive splitters often implies physical fiber degradation in the feeder cable.\n")

    # 库存清单
    inventory = [
        {"item": "OLT-X1-Fan-Kit", "stock": 2, "cost": 1200, "compatibility": "OLT-X1"},
        {"item": "Tier1-Splitter-Standard", "stock": 5, "cost": 450, "attenuation_spec": "10dB"},
        {"item": "Transceiver-BX-LowPower", "stock": 10, "cost": 150, "compatibility": "A-Series"},
        {"item": "Transceiver-BX-HighPower", "stock": 0, "cost": 300, "compatibility": "A-Series"}
    ]
    with open("inventory/current_stock.json", "w") as f:
        json.dump(inventory, f, indent=4)

def build_turn_2():
    # 模拟环境变化：新的紧急情况
    os.makedirs("field_reports/node_beta", exist_ok=True)
    with open("field_reports/node_beta/emergency_alert.txt", "w") as f:
        f.write("URGENT: Node Beta backbone link showing intermittent connectivity.\n")
        f.write("Recent vibration sensors triggered near junction J-14.\n")
        f.write("Requirement: We need to reroute at least 40% of Alpha's spare capacity to Beta, but only if Alpha's core units are stabilized.\n")

def build_turn_3():
    # 模拟预算削减和财务审计
    with open("finance_directive.txt", "w") as f:
        f.write("RE: Quarterly Budget Adjustment\n")
        f.write("Due to procurement delays, all maintenance costs for Node Alpha and Beta must be reduced by 20% compared to your initial projection.\n")
        f.write("If you previously suggested hardware replacements, you must now find a way to patch or re-allocate existing resources from the inventory we had at the start.\n")

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
