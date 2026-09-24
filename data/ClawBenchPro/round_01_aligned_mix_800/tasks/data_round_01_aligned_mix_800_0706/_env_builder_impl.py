import os
import json
import csv

def build_env():
    data_dir = "community_garden_data"
    os.makedirs(data_dir, exist_ok=True)
    
    inventory = {
        "Milkweed": {"stock": 50, "is_invasive": False},
        "English Ivy": {"stock": 20, "is_invasive": True},
        "Kudzu": {"stock": 10, "is_invasive": True},
        "Heirloom Tomato": {"stock": 100, "is_invasive": False},
        "Japanese Knotweed": {"stock": 15, "is_invasive": True},
        "Sunflowers": {"stock": 30, "is_invasive": False}
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
