import os
import argparse
import json

def build_turn_1():
    os.makedirs("unprocessed_cases", exist_ok=True)
    
    # 案件1: 典型特征 A
    case_1 = {
        "case_id": "CAS-2024-001",
        "description": "Suspect wearing a dark hoodie, used a crowbar. Stole electronics worth $5000. Left a specific graffiti tag: 'X-Shadow'.",
        "timestamp": "2024-05-01 02:00",
        "witness_sketch": "Male, approx 6ft, left-handed."
    }
    
    # 案件2: 干扰项（看似关联但作案手法不同）
    case_2 = {
        "case_id": "CAS-2024-002",
        "description": "Store window smashed by a brick. Cash register emptied ($800). No specific tags found.",
        "timestamp": "2024-05-01 04:30",
        "witness_sketch": "Short build, wearing a red cap."
    }
    
    # 案件3: 典型特征 A 的变体
    case_3 = {
        "case_id": "CAS-2024-003",
        "description": "Back door pried open with heavy tool. High-end cameras missing ($12000). Found a faint 'X' mark on the alley wall.",
        "timestamp": "2024-05-03 01:15",
        "witness_sketch": "Tall male, hooded, moves with a slight limp."
    }

    with open("unprocessed_cases/case_001.json", "w") as f: json.dump(case_1, f)
    with open("unprocessed_cases/case_002.json", "w") as f: json.dump(case_2, f)
    with open("unprocessed_cases/case_003.json", "w") as f: json.dump(case_3, f)

def build_turn_2():
    os.makedirs("new_evidence", exist_ok=True)
    
    # 新案件：引入新线索“蓝色皮卡”
    case_4 = {
        "case_id": "CAS-2024-004",
        "description": "Warehouse break-in. Blue pickup truck spotted nearby. Suspect limping. Stole copper wiring ($3000).",
        "timestamp": "2024-05-05 23:45"
    }
    
    # 关键矛盾：手机定位数据
    # 这里的经纬度对应的地方其实是警察局，暗示案发时嫌疑人A其实在被询问，或者数据有误
    alibi_data = [
        {"timestamp": "2024-05-03 01:00", "location": "34.0522, -118.2437", "note": "Suspect A Phone Signal"}
    ]
    
    with open("new_evidence/case_004.json", "w") as f: json.dump(case_4, f)
    with open("new_evidence/phone_logs.json", "w") as f: json.dump(alibi_data, f)

def build_turn_3():
    os.makedirs("forensics_lab", exist_ok=True)
    os.makedirs("final_submission", exist_ok=True)
    
    # 实验室报告：反转。指纹证明 Case 1 和 Case 4 是同一个人，但 Case 3 是模仿者。
    lab_results = {
        "fingerprint_matches": {
            "CAS-2024-001": "Match_Suspect_Alpha",
            "CAS-2024-004": "Match_Suspect_Alpha",
            "CAS-2024-003": "Match_Suspect_Beta"
        },
        "fiber_analysis": "Blue wool fibers found in Case 4 match the jacket worn by Suspect Alpha in Case 1."
    }
    
    with open("forensics_lab/lab_results.json", "w") as f: json.dump(lab_results, f)

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
