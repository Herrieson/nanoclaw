import os
import json
import random
import datetime

def build_env():
    # Setup directories
    base_notes_dir = "messy_desk/notes"
    roster_dir = "messy_desk/patient_roster"
    os.makedirs(base_notes_dir, exist_ok=True)
    os.makedirs(roster_dir, exist_ok=True)
    os.makedirs("organized_desk", exist_ok=True)

    random.seed(1677)

    # 1. Generate Roster
    first_names = ["Arthur", "Sarah", "Martha", "Billy", "Chloe", "Dave", "Greg", "Emma", "Liam", "Olivia", "Noah", "Ava", "William"]
    last_names = ["Pendelton", "Jenkins", "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    
    roster = []
    patients = {} # id -> info
    for i in range(1, 151):
        pid = f"P{i:03d}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        care_type = random.choice(["Residential", "Residential", "Outpatient", "Discharged"])
        roster.append({
            "patient_id": pid,
            "full_name": name,
            "care_category": care_type
        })
        patients[pid] = {"name": name, "type": care_type}
        
    with open(os.path.join(roster_dir, "master_roster.json"), "w", encoding="utf-8") as f:
        json.dump(roster, f, indent=4)

    # 2. Generate Fragmented Notes across a year
    start_date = datetime.date(2023, 1, 1)
    
    keywords = ["stressed", "tense", "anxious", "yoga", "meditation"]
    distractors = ["happy", "tired", "recovering well", "ate a big meal", "family visited", "sleeping okay"]
    
    note_templates = [
        "Patient ID: {pid}. ROM check normal. Pain is {pain}/10 today. Observation: {obs}\n",
        "Saw {pid} in the afternoon. pain_level={pain}. They seem {obs}.\n",
        '{{"id": "{pid}", "vitals": "stable", "pain_score": {pain}, "notes": "{obs}"}}',
        "Note for {pid} - {obs}. Complains of pain level {pain}/10. Needs follow up.",
        "[{pid}] Routine check. pain:{pain} . Patient was doing {obs}."
    ]

    # Generate ~800 daily records scattered in deep paths
    for _ in range(800):
        # Pick a random date
        delta_days = random.randint(0, 360)
        curr_date = start_date + datetime.timedelta(days=delta_days)
        
        # Build path: YYYY/MM/DD
        year_str = str(curr_date.year)
        month_str = f"{curr_date.month:02d}"
        day_str = f"{curr_date.day:02d}"
        
        day_path = os.path.join(base_notes_dir, year_str, month_str, day_str)
        os.makedirs(day_path, exist_ok=True)
        
        # Pick a random patient
        pid = f"P{random.randint(1, 150):03d}"
        
        # Generate data
        pain = random.randint(1, 10)
        
        # 30% chance to include a mindfulness keyword
        if random.random() < 0.3:
            obs = random.choice(keywords)
            # Mixed case to test case-insensitivity
            if random.random() < 0.5:
                obs = obs.upper()
            elif random.random() < 0.5:
                obs = obs.capitalize()
        else:
            obs = random.choice(distractors)
            
        template = random.choice(note_templates)
        content = template.format(pid=pid, pain=pain, obs=obs)
        
        # Add random noise lines to some files
        if random.random() < 0.2:
            content = "SYS_SYNC_ERROR: Retry in 5s...\n" + content + "\nEND_OF_TRANSMISSION"
            
        # Random extensions
        ext = random.choice([".txt", ".log", ".json", ".synctemp", ".dat"])
        device = random.choice(["tablet", "phone", "pc", "watch"])
        filename = f"{device}_sync_{random.randint(1000,9999)}{ext}"
        
        file_path = os.path.join(day_path, filename)
        
        # Write file (append if exists to create mixed files)
        mode = "a" if os.path.exists(file_path) else "w"
        with open(file_path, mode, encoding="utf-8") as f:
            f.write(content + "\n")

if __name__ == "__main__":
    build_env()
