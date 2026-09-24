import os
import argparse
import json
import csv
import random

def build_turn_1():
    # 供应商数据
    os.makedirs("procurement", exist_ok=True)
    vendors = [
        {"name": "Kinshasa_Solar_Tech", "cost": 8500, "efficiency": 0.18, "lifespan_years": 5, "reviews": "Good service, but batteries get hot."},
        {"name": "Global_Energy_Corp", "cost": 12000, "efficiency": 0.22, "lifespan_years": 8, "reviews": "Expensive but reliable."},
        {"name": "EcoVanguard", "cost": 7000, "efficiency": 0.15, "lifespan_years": 3, "reviews": "Cheap parts, frequent failures reported in humid areas."}, # 毒药选项
        {"name": "Lualaba_Power", "cost": 9200, "efficiency": 0.20, "lifespan_years": 6, "reviews": "Solid mid-range choice."}
    ]
    with open("procurement/vendors.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=vendors[0].keys())
        writer.writeheader()
        writer.writerows(vendors)

    # 历史用电记录 (带脏数据和异常点)
    os.makedirs("usage_logs", exist_ok=True)
    usage_data = []
    for day in range(1, 31):
        usage_data.append({
            "day": day,
            "school_main_building_kwh": round(random.uniform(20, 25), 2),
            "lab_kwh": round(random.uniform(10, 15), 2),
            "dorm_kwh": round(random.uniform(15, 30), 2)
        })
    with open("usage_logs/history_october.json", "w") as f:
        json.dump(usage_data, f, indent=4)

    # 技术文档：关于逆变器的隐蔽规则
    with open("procurement/inverter_specs.txt", "w") as f:
        f.write("System Type: DC-Coupled\n")
        f.write("Inverter Model: Vulcan-X1\n")
        f.write("Max Input Voltage: 450V\n")
        f.write("Compatibility Rule: Must use pure sine wave components for medical equipment integration.\n")

def build_turn_2():
    # 模拟运行一个月后的数据
    os.makedirs("usage_logs/current_month", exist_ok=True)
    current_usage = []
    # 故意制造故障点：温度过高导致效率下降
    for day in range(1, 15):
        temp = 35 + day * 0.5
        efficiency_loss = 0.02 if temp > 40 else 0
        current_usage.append({
            "day": day,
            "temp_celsius": temp,
            "output_kwh": round(40 * (1 - efficiency_loss), 2),
            "load_kwh": 45,
            "status": "Critical" if temp > 42 else "Stable"
        })
    with open("usage_logs/current_month/runtime_telemetry.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=current_usage[0].keys())
        writer.writeheader()
        writer.writerows(current_usage)

def build_turn_3():
    # 扩容选项
    os.makedirs("expansion_options", exist_ok=True)
    options = [
        {"mod_name": "HealthGrid_Addon_A", "output_boost": "15kWh", "wave_type": "Modified Sine", "price": 2000}, # 与医疗设备冲突（见Turn 1文档）
        {"mod_name": "HealthGrid_Addon_B", "output_boost": "12kWh", "wave_type": "Pure Sine", "price": 3500} # 唯一可行但贵
    ]
    with open("expansion_options/specs.json", "w") as f:
        json.dump(options, f, indent=4)
    
    # 卫生站的需求文档
    with open("expansion_options/clinic_requirements.txt", "w") as f:
        f.write("Mandatory: Clinic requires stable 10kWh daily for vaccine refrigeration.\n")
        f.write("Warning: Refrigerators are sensitive to wave distortion.\n")

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
