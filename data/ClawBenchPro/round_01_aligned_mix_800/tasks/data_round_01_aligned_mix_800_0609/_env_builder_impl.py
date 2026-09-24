import os
import json
import csv

def build_env():
    os.makedirs("docs", exist_ok=True)
    
    trails = [
        {"name": "Devil's Backbone", "difficulty": "Hard", "length_miles": 12.5, "elevation_gain_ft": 3000},
        {"name": "Pine Needles Path", "difficulty": "Moderate", "length_miles": 4.0, "elevation_gain_ft": 800},
        {"name": "Little Bear Loop", "difficulty": "Easy", "length_miles": 2.8, "elevation_gain_ft": 150},
        {"name": "Eagle Point", "difficulty": "Easy", "length_miles": 5.5, "elevation_gain_ft": 400},
        {"name": "Boulder Scramble", "difficulty": "Hard", "length_miles": 1.5, "elevation_gain_ft": 1200}
    ]
    with open("docs/trails_db.json", "w", encoding="utf-8") as f:
        json.dump(trails, f, indent=2)
        
    gear = [
        {"item": "Family Tent", "weight_oz": 150.5, "status": "Packed"},
        {"item": "Sleeping Bag Adult 1", "weight_oz": 45.0, "status": "Needed"},
        {"item": "Sleeping Bag Adult 2", "weight_oz": 45.0, "status": "Needed"},
        {"item": "Toddler Sleeping Bag", "weight_oz": 25.5, "status": "Needed"},
        {"item": "Camp Stove", "weight_oz": 16.0, "status": "Packed"},
        {"item": "Water Filter", "weight_oz": 12.0, "status": "Needed"},
        {"item": "Aircraft-grade Aluminum Stakes", "weight_oz": 8.0, "status": "Needed"},
        {"item": "First Aid Kit", "weight_oz": 22.0, "status": "Needed"},
        {"item": "Hiking Boots", "weight_oz": 40.0, "status": "Packed"}
    ]
    with open("docs/garage_gear.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["item", "weight_oz", "status"])
        writer.writeheader()
        writer.writerows(gear)

if __name__ == "__main__":
    build_env()
