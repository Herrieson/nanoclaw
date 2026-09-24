import os
import json
import csv
import random

def build_env():
    # Seed for determinism
    random.seed(962)
    
    # 1. Create Directories
    dirs_to_make = [
        "admin_records/enrollment_2021",
        "admin_records/enrollment_2023",
        "reference_materials/archives",
        "reference_materials/current",
        "student_submissions/ipad_sync/week1",
        "student_submissions/usb_drive/corrupted_folder",
        "student_submissions/email_attachments",
    ]
    for d in dirs_to_make:
        os.makedirs(d, exist_ok=True)
        
    # 2. Build Rosters (Noise + Real)
    old_roster = [{"name": f"Old_Student_{i}", "status": "enrolled"} for i in range(10)]
    with open("admin_records/enrollment_2021/roster.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "status"])
        writer.writeheader()
        writer.writerows(old_roster)

    # 40 enrolled, 15 dropped
    enrolled_names = [
        "Alice", "Bob", "Charlie", "Daisy", "Ethan", "Fiona", "George", "Hannah",
        "Ian", "Julia", "Kevin", "Liam", "Mia", "Noah", "Olivia", "Paul", "Quinn",
        "Rachel", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xander", "Yara", "Zack",
        "Aaron", "Bella", "Caleb", "Diana", "Eli", "Faith", "Gavin", "Holly", "Isaac",
        "Jade", "Kyle", "Luna", "Mason", "Nora"
    ]
    dropped_names = ["Xavier", "Yvonne", "Zane", "Arthur", "Betty", "Carl", "Doris", "Earl", "Fran", "Gary", "Helen", "Ivan", "Jane", "Karl", "Leo"]
    
    current_roster = [{"name": n, "status": "enrolled"} for n in enrolled_names] + \
                     [{"name": n, "status": "dropped"} for n in dropped_names]
    random.shuffle(current_roster)
    
    with open("admin_records/enrollment_2023/roster.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "status"])
        writer.writeheader()
        writer.writerows(current_roster)

    # 3. Build Plant Guides
    old_guide = {
        "status": "deprecated_2015",
        "plants": {
            "Sego Lily": "native",
            "Sagebrush": "invasive", # Wrong in old guide
            "Russian Thistle": "invasive",
            "Cheatgrass": "native", # Wrong in old guide
            "Dandelion": "invasive",
            "Bitterbrush": "native"
        }
    }
    official_guide = {
        "status": "official_2023",
        "metadata": "Approved by district board",
        "plants": {
            "Sego Lily": "native",
            "Sagebrush": "native",
            "Russian Thistle": "invasive",
            "Cheatgrass": "invasive",
            "Dandelion": "invasive",
            "Bitterbrush": "native",
            "Blue Flax": "native",
            "Fireweed": "native",
            "Knapweed": "invasive"
        }
    }
    
    with open("reference_materials/archives/guide_2015.json", "w") as f:
        json.dump(old_guide, f, indent=4)
        
    with open("reference_materials/current/district_plant_guide_v2.json", "w") as f:
        json.dump(official_guide, f, indent=4)
        
    # Fake guide as a distractor
    with open("reference_materials/current/unofficial_draft.json", "w") as f:
        json.dump({"status": "draft", "plants": {"Rose": "native"}}, f, indent=4)

    # 4. Generate Submissions
    # We will intentionally make 7 enrolled students "missing" (no logs anywhere)
    missing_students = ["Alice", "Fiona", "Kevin", "Sam", "Wendy", "Eli", "Luna"]
    active_students = [n for n in enrolled_names if n not in missing_students]
    
    all_plants = list(official_guide["plants"].keys())
    
    # Let's generate a pool of logs
    logs = []
    # Valid logs for enrolled students
    for student in active_students:
        num_logs = random.randint(1, 4)
        for _ in range(num_logs):
            logs.append({
                "student": student,
                "plant": random.choice(all_plants),
                "growth_inches": round(random.uniform(0.5, 12.0), 2)
            })
            
    # Noise logs for dropped students
    for student in dropped_names:
        if random.random() > 0.5:
            logs.append({
                "student": student,
                "plant": random.choice(all_plants),
                "growth_inches": round(random.uniform(1.0, 10.0), 2)
            })
            
    # Noise logs for completely random people not on roster
    for _ in range(15):
        logs.append({
            "student": f"Ghost_Student_{random.randint(1,99)}",
            "plant": random.choice(all_plants),
            "growth_inches": round(random.uniform(1.0, 5.0), 2)
        })

    random.shuffle(logs)
    
    # Distribute logs into different files and formats
    # Chunk 1: CSV in ipad_sync
    chunk1 = logs[:len(logs)//3]
    with open("student_submissions/ipad_sync/week1/export_01.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["student", "plant", "growth_inches"])
        writer.writeheader()
        writer.writerows(chunk1)
        
    # Chunk 2: JSON in usb_drive
    chunk2 = logs[len(logs)//3 : 2*len(logs)//3]
    with open("student_submissions/usb_drive/corrupted_folder/recovered_logs.json", "w") as f:
        json.dump(chunk2, f, indent=4)
        
    # Chunk 3: TXT in email_attachments
    chunk3 = logs[2*len(logs)//3:]
    with open("student_submissions/email_attachments/raw_notes.txt", "w") as f:
        for log in chunk3:
            f.write(f"Student: {log['student']} | Plant: {log['plant']} | Growth: {log['growth_inches']}\n")
            
    # Sprinkle some purely noise files that agent should ignore without crashing
    with open("student_submissions/email_attachments/grandkids_photo.txt", "w") as f:
        f.write("Just a text file pretending to be a photo. No plant data here!\nStudent: None | Plant: None | Growth: NaN")
        
if __name__ == "__main__":
    build_env()
