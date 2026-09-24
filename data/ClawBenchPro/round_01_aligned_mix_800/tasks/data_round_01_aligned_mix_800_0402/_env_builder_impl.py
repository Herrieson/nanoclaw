import os
import json
import csv
import random
import datetime

def build_env():
    # Set seed for reproducible wasteland
    random.seed(1152)
    
    # Create base directories
    base_dir = "data_export"
    rosters_dir = os.path.join(base_dir, "rosters")
    active_aliases_dir = os.path.join(base_dir, "active_aliases")
    archived_aliases_dir = os.path.join(base_dir, "archived_aliases")
    logs_dir = os.path.join(base_dir, "logs")
    
    for d in [rosters_dir, active_aliases_dir, archived_aliases_dir, logs_dir]:
        os.makedirs(d, exist_ok=True)

    # Name generation parts
    first_names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Oliver", "Isabella", "Elijah", "Sophia", "James",
                   "Mia", "William", "Charlotte", "Benjamin", "Amelia", "Lucas", "Harper", "Henry", "Evelyn", "Theodore",
                   "Leo", "Emily", "Chloe", "Robert", "Mia", "Zoe", "Jack", "Lily", "Luke", "Grace"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                  "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"]

    # Generate 300 unique names
    all_names = list(set([f"{f} {l}" for f in first_names for l in last_names]))
    random.shuffle(all_names)
    
    final_roster_names = all_names[:200]
    old_roster_names = all_names[200:250]
    unregistered_names = all_names[250:280]

    # Generate IDs
    final_roster = [{"student_id": str(1000 + i), "official_name": name, "grade": 5} for i, name in enumerate(final_roster_names)]
    old_roster = [{"student_id": str(9000 + i), "official_name": name, "grade": 6} for i, name in enumerate(old_roster_names)]

    # Write Rosters
    with open(os.path.join(rosters_dir, "roster_FINAL_v3.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["student_id", "official_name", "grade"])
        writer.writeheader()
        writer.writerows(final_roster)
        
    with open(os.path.join(rosters_dir, "roster_2022.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["student_id", "official_name", "grade"])
        writer.writeheader()
        writer.writerows(old_roster)
        
    with open(os.path.join(rosters_dir, "roster_v1_draft.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["student_id", "official_name", "grade"])
        writer.writeheader()
        writer.writerows(final_roster[:50]) # Incomplete draft

    # Generate Aliases
    adjectives = ["Cool", "Super", "Ghost", "Ninja", "Star", "Cyber", "Dark", "Pro", "Mega", "Hyper"]
    nouns = ["Rider", "Wizard", "Gamer", "Wolf", "Dragon", "Cat", "Bear", "Phoenix", "Sniper", "King"]
    
    active_aliases = {}
    # Assign aliases to 150 valid students
    for student in final_roster[:150]:
        alias = f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(10, 99)}"
        active_aliases[alias] = student["official_name"]

    archived_aliases = {}
    # Assign aliases to old students
    for student in old_roster:
        alias = f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(10, 99)}"
        archived_aliases[alias] = student["official_name"]
    # Add some conflicting aliases in archived just to trap those who don't read instructions
    for alias in list(active_aliases.keys())[:10]:
        archived_aliases[alias] = "WRONG_MAPPED_NAME"

    # Split active aliases into 3 files to fragment data
    items = list(active_aliases.items())
    for i in range(3):
        chunk = dict(items[i*50 : (i+1)*50])
        with open(os.path.join(active_aliases_dir, f"mapping_part_{i+1}.json"), "w", encoding="utf-8") as f:
            json.dump(chunk, f, indent=4)
            
    with open(os.path.join(archived_aliases_dir, "old_aliases_2022.json"), "w", encoding="utf-8") as f:
        json.dump(archived_aliases, f, indent=4)

    # Generate Logs
    start_date = datetime.date(2023, 10, 1)
    modules = ["math", "math", "math", "math", "reading", "science", "math_fun", "math_prep", "history", "art"]
    
    # We will generate 20 days of logs
    for day_offset in range(20):
        current_date = start_date + datetime.timedelta(days=day_offset)
        day_dir = os.path.join(logs_dir, current_date.strftime("%Y-%m-%d"))
        os.makedirs(day_dir, exist_ok=True)
        
        # 30 files per day
        for file_idx in range(30):
            num_records = random.randint(3, 15)
            records = []
            for _ in range(num_records):
                # Decide user representation
                user_type = random.random()
                if user_type < 0.3:
                    # official name
                    user_val = random.choice(final_roster)["official_name"]
                elif user_type < 0.6:
                    # student id
                    user_val = random.choice(final_roster)["student_id"]
                elif user_type < 0.85:
                    # alias
                    user_val = random.choice(list(active_aliases.keys()))
                else:
                    # noise / unregistered / old
                    user_val = random.choice(unregistered_names + list(archived_aliases.keys()))

                record = {
                    "user": user_val,
                    "module": random.choice(modules),
                    "time_spent_min": random.randint(5, 45),
                    "score": random.randint(40, 100)
                }
                records.append(record)

            file_path = os.path.join(day_dir, f"session_{file_idx}.json")
            
            # 10% chance to be a corrupted file
            is_corrupt = random.random() < 0.1
            
            if is_corrupt:
                json_str = json.dumps(records, indent=4)
                # Cut the string midway
                cut_point = len(json_str) // 2
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(json_str[:cut_point])
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(records, f, indent=4)

if __name__ == "__main__":
    build_env()
