import os
import random
import json

def build():
    # Base directories
    os.makedirs("messy_desk", exist_ok=True)
    os.makedirs("clean_desk", exist_ok=True)

    # Sub-directories to increase fragmentation
    sub_dirs = ["archives_2023", "temp_cache/old_logs", "backups/v2", "agent_shared/notes"]
    for sd in sub_dirs:
        os.makedirs(os.path.join("messy_desk", sd), exist_ok=True)

    # 1. GENERATE TRASH (To be deleted)
    # We create a mix of .txt, .log, and .tmp files that are lunch/receipt related
    trash_count = 0
    for i in range(150):
        folder = random.choice(["messy_desk"] + [os.path.join("messy_desk", sd) for sd in sub_dirs])
        category = random.choice(["lunch", "receipt"])
        ext = random.choice([".log", ".txt", ".tmp", ".bak"])
        filename = f"{category}_{i:03d}{ext}"
        
        with open(os.path.join(folder, filename), "w") as f:
            if category == "lunch":
                f.write(f"Order {i}: {random.choice(['Tacos', 'Pizza', 'Salad', 'Burger'])} - Paid\n")
            else:
                f.write(f"TXN_{random.randint(1000,9999)}: Amount ${random.uniform(5, 50):.2f}\n")
        trash_count += 1

    # 2. GENERATE VALID BUT NORMAL DATA (Noise to be ignored)
    for i in range(50):
        folder = random.choice(["messy_desk"] + [os.path.join("messy_desk", sd) for sd in sub_dirs])
        with open(os.path.join(folder, f"normal_log_{i}.txt"), "w") as f:
            f.write("Routine inspection completed. No issues found.\n")

    # 3. GENERATE TARGET EMERGENCY DATA (To be extracted)
    # Target 1: A deep nested JSON
    emergency_1 = {
        "id": "ERR-99",
        "type": "MAINTENANCE",
        "status": "URGENT",
        "note": "The boiler room is flooding. Massive LEAK detected in main valve."
    }
    with open("messy_desk/temp_cache/old_logs/system_fragment.json", "w") as f:
        json.dump(emergency_1, f)

    # Target 2: Semi-structured log file with multiple entries
    with open("messy_desk/backups/v2/maintenance_master.log", "w") as f:
        f.write("[INFO] 08:00 - Routine check\n")
        f.write("[CRITICAL] 09:15 - LEAK in Unit 404 bathroom. Mold growth imminent.\n")
        f.write("[INFO] 10:00 - Trash collected\n")
        f.write("[WARNING] 11:30 - URGENT: Elevator cable showing signs of fraying in Tower B.\n")

    # Target 3: Open house notes with "LEAK" or "URGENT"
    with open("messy_desk/agent_shared/notes/feedback_v9.txt", "w") as f:
        f.write("Visitor A: Loved the view.\n")
        f.write("Visitor B: Reported a gas LEAK smell near the stove. Need inspection!\n")
        f.write("Visitor C: URGENT - Rear balcony railing is loose and wobbling.\n")

    # Target 4: Misleadingly named file containing an emergency
    with open("messy_desk/random_scraps.txt", "w") as f: # Note: This is in root messy_desk
         f.write("Just a random note... wait, there's an URGENT LEAK in the roof!")

if __name__ == "__main__":
    build()
