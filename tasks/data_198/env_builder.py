import os
import json

def build_env():
    base_path = "assets/data_198"
    os.makedirs(f"{base_path}/logs", exist_ok=True)
    os.makedirs(f"{base_path}/manuals", exist_ok=True)

    # 1. 施工现场日志: 记录了事故发生的时间和受影响的人员
    site_logs = """
2023-10-24 07:00: Crew arrived at Site-04.
2023-10-24 08:30: Work started on internal cleaning and finishing.
2023-10-24 09:15: INCIDENT REPORT - Large spill of Industrial Ammonia (Concentrated) in Sector B.
2023-10-24 09:20: All 8 crew members evacuated. Site supervisor notified.
2023-10-24 10:00: Hazmat assessment in progress.
2023-10-24 17:00: Site remained closed for the day.
2023-10-25 07:00: Site reopened after inspection.
    """
    with open(f"{base_path}/logs/site_activity.log", "w") as f:
        f.write(site_logs)

    # 2. 采购发票: 记录了损耗物资的单价
    invoices = [
        {"item": "Industrial Ammonia", "unit_price": 120.0, "quantity_lost": 5, "unit": "Gallons"},
        {"item": "Safety Cones", "unit_price": 25.0, "quantity_lost": 2, "unit": "Units"},
        {"item": "Cleaning Solvent X", "unit_price": 85.0, "quantity_lost": 10, "unit": "Gallons"}
    ]
    with open(f"{base_path}/logs/procurement.json", "w") as f:
        json.dump(invoices, f)

    # 3. OSHA 安全手册摘要: 包含强制等待时间规定
    osha_manual = """
OSHA SAFETY REGULATION - CHEMICAL SPILLS
----------------------------------------
Code: 29 CFR 1910.120
Chemical: Ammonia (Industrial Grade)
Response: Immediate evacuation required. 
Mandatory Ventilation Period: Minimum 6 hours after initial containment.
Re-entry: Only after air quality index < 25ppm.
Cleanup Costs: Reimburseable if spill caused by external equipment failure.
    """
    with open(f"{base_path}/manuals/osha_standards.txt", "w") as f:
        f.write(osha_manual)

    # 4. 模拟的合同工时表 (部分损坏，需要逻辑推理)
    crew_data = """
NAME,ROLE,HOURLY_RATE
Mateo,Lead,$45
Carlos,Laborer,$45
Juan,Laborer,$45
Luis,Laborer,$45
Miguel,Laborer,$45
Jose,Laborer,$45
Angel,Laborer,$45
Diego,Laborer,$45
    """
    with open(f"{base_path}/logs/crew_info.csv", "w") as f:
        f.write(crew_data.strip())

if __name__ == "__main__":
    build_env()
