import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("raw_data", exist_ok=True)
    
    # 员工数据：包含技能等级、特殊属性
    staff = [
        {"id": "S001", "name": "Officer Banks", "skill": 5, "tags": "expert,night_owl", "salary": 25},
        {"id": "S002", "name": "Officer Chen", "skill": 3, "tags": "medic", "salary": 20},
        {"id": "S003", "name": "Officer Miller", "skill": 4, "tags": "tech_savvy", "salary": 22},
        {"id": "S004", "name": "Officer Davis", "skill": 2, "tags": "newbie", "salary": 18},
        {"id": "S005", "name": "Officer Wilson", "skill": 5, "tags": "expert,k9", "salary": 28},
    ]
    with open("raw_data/staff_list.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=staff[0].keys())
        writer.writeheader()
        writer.writerows(staff)

    # 复杂约束逻辑
    constraints = {
        "logic_redlines": [
            "Officer Banks and Officer Miller cannot work the same shift due to personal conflicts.",
            "Any area marked 'High Risk' must have at least one staff with skill >= 4.",
            "Maximum continuous working hours: 8 hours.",
            "The 'Med Center' must always have a staff with the 'medic' tag."
        ],
        "area_weights": {
            "Main Gate": "Medium",
            "Vinyl Exhibition": "High Risk",
            "Med Center": "Low",
            "Student Union": "Medium"
        }
    }
    with open("raw_data/constraints.json", "w") as f:
        json.dump(constraints, f, indent=4)

    # 地形约束：干扰项较多
    site_access = """
    Gate_A: Open
    Gate_B: CLOSED (Construction)
    Hallway_C: Restricted after 22:00
    Elevator_D: Staff only
    Tunnel_E: FLOODED - DO NOT USE
    """
    with open("raw_data/site_access.txt", "w") as f:
        f.write(site_access)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    # 突发事件：人员受伤和地点变动
    incidents = {
        "absentees": ["S002"], # Medic 缺失，迫使 Agent 寻找替代方案或调整逻辑
        "building_status": {
            "Building_2": "CLOSED_FOR_MAINTENANCE",
            "Command_Center_Relocation": "Move to Vinyl Exhibition Room B"
        },
        "new_rule_leak": "University board demands no one works more than 12 hours total in the first 3 days."
    }
    with open("updates/incidents_report.json", "w") as f:
        json.dump(incidents, f, indent=4)

def build_turn_3():
    os.makedirs("updates", exist_ok=True)
    # 智报：高危区域与路径冲突
    intelligence = """
    REPORT: Potential disruption suspected near Vinyl Exhibition - North Wing.
    SENSITIVE_ZONES: ["Zone_X", "Zone_Y"]
    PATH_BLOCKAGE: The path between Main Gate and Zone_X is under surveillance, do not use for routine patrol.
    EMERGENCY_REQUIREMENT: Any incident response team must consist of at least 2 people with combined skill > 7.
    """
    with open("updates/intelligence.txt", "w") as f:
        f.write(intelligence)

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
