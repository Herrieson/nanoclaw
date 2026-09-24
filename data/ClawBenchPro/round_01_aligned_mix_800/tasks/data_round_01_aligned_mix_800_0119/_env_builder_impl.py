import os
import json
import csv
import argparse

def build_turn_1():
    os.makedirs("blueprints", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 制造库存刀具数据
    tools = [
        {"tool_id": "T001", "tool_type": "EndMill", "radius": 6, "cost": 10},
        {"tool_id": "T002", "tool_type": "EndMill", "radius": 8, "cost": 20},
        {"tool_id": "T003", "tool_type": "Drill", "radius": 3, "cost": 5},
        {"tool_id": "T004", "tool_type": "Drill", "radius": 4, "cost": 8},
        {"tool_id": "T005", "tool_type": "Lathe", "radius": 10, "cost": 15},
        {"tool_id": "T006", "tool_type": "EndMill", "radius": 7, "cost": 12},
        {"tool_id": "T007", "tool_type": "Lathe", "radius": 11, "cost": 18},
    ]
    with open("inventory/tools.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["tool_id", "tool_type", "radius", "cost"])
        writer.writeheader()
        writer.writerows(tools)

    # 制造订单图纸数据
    blueprints = [
        # ORD-01 会优先选用 T001 (cost=10)，若 T001 坏了，由于 radius=6 只有 T001 满足(T006是7)，所以可能会没刀可用，或者如果范围改了...
        # 设定：min=5, max=10。可用: T001(6, c=10), T006(7, c=12), T002(8, c=20)。会选 T001。
        {"order_id": "ORD-01", "required_tool_type": "EndMill", "min_radius": 5, "max_radius": 10, "material": "STEEL-A", "machining_time_hours": 4},
        # ORD-02 选用 T003 (cost=5)
        {"order_id": "ORD-02", "required_tool_type": "Drill", "min_radius": 2, "max_radius": 5, "material": "ALUM-B", "machining_time_hours": 2},
        # ORD-03 是 T3 的毒药！选 T006 (cost=12)
        {"order_id": "ORD-03", "required_tool_type": "EndMill", "min_radius": 6, "max_radius": 9, "material": "TITAN-X", "machining_time_hours": 5},
        # ORD-04 选用 T005 (cost=15)
        {"order_id": "ORD-04", "required_tool_type": "Lathe", "min_radius": 8, "max_radius": 12, "material": "STEEL-A", "machining_time_hours": 6},
    ]
    
    for bp in blueprints:
        with open(f"blueprints/{bp['order_id']}.json", "w") as f:
            json.dump(bp, f, indent=2)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    os.makedirs("blueprints/urgent", exist_ok=True)

    # 损坏的刀具
    with open("updates/broken_tools.txt", "w") as f:
        f.write("T001\n") # T001 损坏，ORD-01 需要重新找刀。本来会选 T006，但 T006 被 ORD-03 占了，所以只能选 T002(cost=20)
        f.write("T003\n") # T003 损坏，ORD-02 需要重新找刀，选 T004(cost=8)

    # 急单，抢占资源
    urgent_blueprints = [
        # 急单 URG-01 需要 EndMill，范围 7-10。当前可用: T002, T006。
        # T006 比较便宜(12)，URG-01 会抢走 T006。导致原来的 ORD-03 被迫寻找新刀具。
        # ORD-03 只能用 T002。而 ORD-01 因为 T001 坏了，也需要刀，可能导致某些单子无法完成。
        {"order_id": "URG-01", "required_tool_type": "EndMill", "min_radius": 7, "max_radius": 10, "material": "BRASS-C", "machining_time_hours": 3},
    ]
    
    for bp in urgent_blueprints:
        with open(f"blueprints/urgent/{bp['order_id']}.json", "w") as f:
            json.dump(bp, f, indent=2)

def build_turn_3():
    with open("supplier_notice.txt", "w") as f:
        f.write("URGENT NOTICE TO ALL MACHINING SHOPS:\n")
        f.write("We have detected critical micro-fractures in our recent batch of materials.\n")
        f.write("All processing involving material code 'TITAN-X' must be immediately halted and scrapped.\n")
        f.write("Please calculate your losses.\n")

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
