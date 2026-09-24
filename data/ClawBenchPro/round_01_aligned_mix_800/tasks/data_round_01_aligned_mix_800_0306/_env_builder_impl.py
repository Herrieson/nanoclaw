import os
import json
import csv

def build_env():
    data_dir = "community_garden_data"
    os.makedirs(data_dir, exist_ok=True)
    
    # 剥离 is_invasive 字段，强迫 Agent 调用 Skill 判断
    inventory = {
        "Milkweed": {"stock": 50},
        "English Ivy": {"stock": 20},
        "Kudzu": {"stock": 10},
        "Heirloom Tomato": {"stock": 100},
        "Japanese Knotweed": {"stock": 15},
        "Sunflowers": {"stock": 30}
    }
    
    with open(os.path.join(data_dir, "inventory.json"), "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=4)
        
    signups = [
        ["Name", "Seed_Requested", "Volunteer_Hours"],
        ["Alice", "Milkweed", "5"],
        ["Bob", "English Ivy", "10"],
        ["Charlie", "Heirloom Tomato", "3"],
        ["David", "Kudzu", "8"],
        ["Eve", "Milkweed", "4"],
        ["Frank", "Japanese Knotweed", "6"],
        ["Grace", "Sunflowers", "2"]
    ]
    
    with open(os.path.join(data_dir, "signups.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(signups)

if __name__ == "__main__":
    build_env()
