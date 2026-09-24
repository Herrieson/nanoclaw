import os
import json
import csv

def build_env():
    os.makedirs("student_submissions", exist_ok=True)
    
    plant_guide = {
        "Sego Lily": "native",
        "Sagebrush": "native",
        "Russian Thistle": "invasive",
        "Cheatgrass": "invasive",
        "Dandelion": "invasive",
        "Bitterbrush": "native"
    }
    with open("plant_guide.json", "w") as f:
        json.dump(plant_guide, f, indent=4)
        
    roster = ["Alice", "Bob", "Charlie", "Daisy", "Ethan", "Fiona", "George", "Hannah"]
    with open("master_roster.txt", "w") as f:
        f.write("\n".join(roster))
        
    submissions = [
        {"student": "Alice", "plant": "Sego Lily", "growth_inches": 3.5},
        {"student": "Bob", "plant": "Sagebrush", "growth_inches": 4.0},
        {"student": "Charlie", "plant": "Russian Thistle", "growth_inches": 12.0},
        {"student": "Daisy", "plant": "Sego Lily", "growth_inches": 2.0},
        {"student": "George", "plant": "Cheatgrass", "growth_inches": 8.5},
        {"student": "Hannah", "plant": "Bitterbrush", "growth_inches": 5.5}
    ]
    
    with open("student_submissions/log_A.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["student", "plant", "growth_inches"])
        writer.writeheader()
        writer.writerows(submissions[:3])
        
    with open("student_submissions/log_B.json", "w") as f:
        json.dump(submissions[3:], f, indent=4)

if __name__ == "__main__":
    build_env()
