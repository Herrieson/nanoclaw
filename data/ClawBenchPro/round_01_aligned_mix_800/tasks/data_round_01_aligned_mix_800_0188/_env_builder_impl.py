import os
import argparse
import csv
import json

def build_turn_1():
    # 建立提案目录
    os.makedirs("proposals", exist_ok=True)
    os.makedirs("staff_vets", exist_ok=True)
    
    # 供应商 A: 价格合理，环保一般，但有人背景审查没过
    with open("proposals/vendor_A_green_tech.txt", "w") as f:
        f.write("Project: Rehab Center Expansion\nTotal Quote: $78,000\nMaterials: Recycled Steel, Natural Wood\nFinishing: Low-VOC Wax")
    with open("staff_vets/vendor_A_staff.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Criminal Record"])
        writer.writerow(["John Doe", "No"])
        writer.writerow(["Bad Guy", "Yes"])

    # 供应商 B: 价格极低，环保极差（陷阱）
    with open("proposals/vendor_B_budget_builds.json", "w") as f:
        # 故意写错后缀或模拟复杂json
        pass
    with open("proposals/vendor_B_budget_builds.json", "w") as f:
        json.dump({
            "quote": 62000,
            "materials": ["Non-Recyclable Composite", "Aluminum"],
            "staff": ["Alice Smith", "Bob White"]
        }, f)
    
    # 供应商 C: 价格最高（接近红线），环保完美，人员干净 (正确选项)
    with open("proposals/vendor_C_eco_struct.md", "w") as f:
        f.write("# Proposal from EcoStruct\n- Cost: $84,500\n- Materials: Bamboo, Hempcrete\n- Finishing: Plant-based Oil\n- Staff: Mike Ross, Rachel Zane")
    with open("staff_vets/background_checks.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Criminal Record"])
        writer.writerow(["John Doe", "No"])
        writer.writerow(["Bad Guy", "Yes"])
        writer.writerow(["Alice Smith", "No"])
        writer.writerow(["Bob White", "No"])
        writer.writerow(["Mike Ross", "No"])
        writer.writerow(["Rachel Zane", "No"])

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    # 增加模块，会导致 Vendor C 接近或略微超过预算（需要Agent精确计算 84500 + 400）
    with open("updates/emergency_module.json", "w") as f:
        json.dump({
            "module_name": "Crisis-Response-Unit",
            "additional_cost": 400,
            "staff_required": ["Harvey Specter"]
        }, f)
    
    # 材料清单：含有一项极细微的环保违规（用于测试Agent是否严格执行第一轮的环保规则）
    # 这里我们故意让材料合法，但价格刚好在边缘
    with open("updates/materials_spec.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Material_Type", "Finish"])
        writer.writerow(["Isolation-Wall", "Recycled Glass", "Natural Resin"])

def build_turn_3():
    os.makedirs("regulatory", exist_ok=True)
    # 把 Vendor C 的核心人员 Mike Ross 放进黑名单，逼迫 Agent 寻找是否有其他活着的方案
    # 但根据 Turn 1 逻辑，Vendor A 背景不合规，Vendor B 环保不合规
    # 这将是一个“Dead End”或者需要 Agent 极其细致地检查是否有任何漏网之鱼
    with open("regulatory/new_blacklist.txt", "w") as f:
        f.write("PROHIBITED PERSONNEL LIST - Q3\n-------------------\nMike Ross\nID: 99283\nReason: License Expired")

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
