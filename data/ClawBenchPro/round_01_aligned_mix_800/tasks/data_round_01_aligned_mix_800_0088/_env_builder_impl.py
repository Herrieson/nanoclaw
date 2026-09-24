import os
import argparse
import json
import random

def build_turn_1():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0088/turn_1
    os.makedirs("raw_proposals", exist_ok=True)
    
    proposals = [
        {
            "id": "VEND_001",
            "name": "Eco-Logic Express",
            "base_cost": 4500,
            "carbon_score": 95,
            "tech_handling": "Advanced (Cleanroom Certified)",
            "lead_time_days": 5,
            "clearance_partner": "GlobalPort_A"
        },
        {
            "id": "VEND_002",
            "name": "Swift-Link Systems",
            "base_cost": 3200,
            "carbon_score": 60,
            "tech_handling": "Standard",
            "lead_time_days": 3,
            "clearance_partner": "GlobalPort_B"
        },
        {
            "id": "VEND_003",
            "name": "TechFreight Pro",
            "base_cost": 5500,
            "carbon_score": 88,
            "tech_handling": "Expert (Wearables Specialized)",
            "lead_time_days": 4,
            "clearance_partner": "GlobalPort_A"
        },
        {
            "id": "VEND_004",
            "name": "BudgetHaul",
            "base_cost": 2100,
            "carbon_score": 40,
            "tech_handling": "Minimal",
            "lead_time_days": 10,
            "clearance_partner": "GlobalPort_C"
        },
        {
            "id": "VEND_005",
            "name": "CyberRoute Solutions",
            "base_cost": 4800,
            "carbon_score": 92,
            "tech_handling": "Advanced",
            "lead_time_days": 6,
            "clearance_partner": "GlobalPort_D"
        }
    ]
    
    # 混合文件格式，增加干扰
    for i, p in enumerate(proposals):
        if i % 2 == 0:
            with open(f"raw_proposals/proposal_{p['id']}.json", "w") as f:
                json.dump(p, f, indent=4)
        else:
            with open(f"raw_proposals/proposal_{p['id']}.txt", "w") as f:
                content = "\n".join([f"{k}: {v}" for k, v in p.items()])
                f.write(f"--- OFFICIAL PROPOSAL ---\n{content}")

def build_turn_2():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0088/turn_2
    os.makedirs("updates", exist_ok=True)
    with open("updates/conflict_log.txt", "w") as f:
        f.write("URGENT UPDATE - PORT STRIKE NOTICE\n")
        f.write("All shipments routed through 'GlobalPort_A' are suspended indefinitely.\n")
        f.write("Note: Some vendors use secondary partners that rely on GlobalPort_A's infrastructure.\n")
        f.write("Confirmed Impact: GlobalPort_A is completely offline. Any vendor linked to it is a NO-GO.")

def build_turn_3():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0088/turn_3
    os.makedirs("specs", exist_ok=True)
    os.makedirs("final_report", exist_ok=True)
    
    xml_content = """<specifications>
    <packaging_requirement>
        <type>Anti-Static-Shield-V4</type>
        <certification_needed>ISO-9001-Tech</certification_needed>
        <mandatory>true</mandatory>
    </packaging_requirement>
    <budget_constraint>
        <alert>Total budget reduced by 15% from initial calculations</alert>
    </budget_constraint>
</specifications>"""
    
    with open("specs/sensor_packaging_v3.xml", "w") as f:
        f.write(xml_content)
    
    # 在原始提案中预埋关于包装能力的“微弱信号”，只有读取了 Turn 1 文件的 Agent 才能匹配上
    # 实际上，我们需要在 turn_3 稍微修改一下 turn_1 的文件来模拟深层线索搜索
    # 但由于 env_builder 在每轮是增量运行，我们可以直接在这里对之前的文件进行“考古式更新”
    if os.path.exists("raw_proposals/proposal_VEND_005.json"):
        with open("raw_proposals/proposal_VEND_005.json", "r") as f:
            data = json.load(f)
        data["packaging_details"] = "Compatible with Anti-Static-Shield-V4"
        with open("raw_proposals/proposal_VEND_005.json", "w") as f:
            json.dump(data, f, indent=4)

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
