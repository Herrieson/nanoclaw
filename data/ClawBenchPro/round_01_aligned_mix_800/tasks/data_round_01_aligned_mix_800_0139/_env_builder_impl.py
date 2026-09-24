import os
import json
import csv
import yaml
import argparse

def build_turn_1():
    os.makedirs("applications", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 陷阱：Booth_2 是Grade B，便宜，如果没注意红线会被选。
    # 陷阱：Booth_4 是Vegan，但非本地，如果优先选本地可能错过它导致无Vegan。
    vendors = [
        {"id": "V01", "name": "Shalom Deli", "cuisine": "Jewish", "is_local": True, "health_grade": "A+", "cost_to_subsidize": 1500, "features": ["Kosher", "Meat"]},
        {"id": "V02", "name": "Dirty Burger", "cuisine": "American", "is_local": True, "health_grade": "B", "cost_to_subsidize": 500, "features": ["Meat"]},
        {"id": "V03", "name": "Green Leaf", "cuisine": "Salad", "is_local": False, "health_grade": "A", "cost_to_subsidize": 1200, "features": ["Vegan"]},
        {"id": "V04", "name": "Colorado BBQ", "cuisine": "BBQ", "is_local": True, "health_grade": "A", "cost_to_subsidize": 2000, "features": ["Meat"]},
        {"id": "V05", "name": "Sweet Treats", "cuisine": "Bakery", "is_local": True, "health_grade": "A", "cost_to_subsidize": 1100, "features": ["Dessert", "Vegetarian"]},
        {"id": "V06", "name": "Taco Town", "cuisine": "Mexican", "is_local": True, "health_grade": "A", "cost_to_subsidize": 1300, "features": ["Meat"]},
        {"id": "V07", "name": "Zen Vegan", "cuisine": "Asian", "is_local": True, "health_grade": "A+", "cost_to_subsidize": 2500, "features": ["Vegan"]},
        {"id": "V08", "name": "Big Pizza", "cuisine": "Italian", "is_local": False, "health_grade": "A", "cost_to_subsidize": 900, "features": ["Vegetarian"]}
    ]

    for v in vendors:
        with open(f"applications/{v['id']}.json", "w") as f:
            json.dump(v, f, indent=4)

    with open("zones.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["zone_id", "capacity", "description"])
        writer.writerow(["Zone_A", "3", "Main Plaza"])
        writer.writerow(["Zone_B", "4", "South Garden"])
        writer.writerow(["Zone_C", "2", "East Alley"])

def build_turn_2():
    os.makedirs("late_applications", exist_ok=True)
    
    # 突发事件：Zone A 淹水，容量变为 0。总容量急剧下降，逼迫重新洗牌。
    with open("urgent_memo.txt", "w") as f:
        f.write("URGENT UPDATE FROM FACILITIES:\nA main water pipe burst under the Main Plaza (Zone_A). The entire zone is flooded and structurally unsafe. Its capacity is now exactly 0. All booths must be relocated to other available zones.\n")

    # 新增申请者
    # V09 是又便宜又是本地的 Vegan，可能是为了替换极贵的 V07 或者非本地的 V03
    late_vendors = [
        {"id": "V09", "name": "Local Roots", "cuisine": "Salad", "is_local": True, "health_grade": "A", "cost_to_subsidize": 1000, "features": ["Vegan"]},
        {"id": "V10", "name": "NY Pastrami", "cuisine": "Jewish", "is_local": False, "health_grade": "A+", "cost_to_subsidize": 1400, "features": ["Kosher", "Meat"]}
    ]

    for v in late_vendors:
        with open(f"late_applications/{v['id']}.json", "w") as f:
            json.dump(v, f, indent=4)

def build_turn_3():
    vips = {
        "Mayor_Smith": {
            "title": "Mayor",
            "free_time_start": "13:00",
            "free_time_end": "15:00",
            "preferences": {
                "must_be_local": True,
                "avoid_features": ["Vegan"]
            }
        },
        "Councilwoman_Goldberg": {
            "title": "Lead Councilwoman",
            "free_time_start": "14:00",
            "free_time_end": "16:00",
            "preferences": {
                "must_have_features": ["Kosher", "Dessert"] # 需分别访问两个不同的摊位涵盖这些特征
            }
        }
    }
    
    with open("vips.json", "w") as f:
        json.dump(vips, f, indent=4)

    transit_times = {
        "Zone_A_to_Zone_B": 5,
        "Zone_B_to_Zone_A": 5,
        "Zone_B_to_Zone_C": 15,
        "Zone_C_to_Zone_B": 15,
        "Zone_A_to_Zone_C": 20,
        "Zone_C_to_Zone_A": 20,
        "Same_Zone": 2
    }
    
    with open("transit_times.yaml", "w") as f:
        yaml.dump(transit_times, f)

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
