import os
import json
import csv
import random

def build_env():
    random.seed(42) # Ensure deterministic environment generation
    
    # 1. Generate the messy IT system roster export
    valid_students = []
    dropped_students = []
    other_class_students = []
    
    # 20 valid students, 10 dropped, 30 other classes
    for i in range(1, 21): valid_students.append(f"Student_AP_{i}")
    for i in range(1, 11): dropped_students.append(f"Student_Drop_{i}")
    for i in range(1, 31): other_class_students.append(f"Student_Other_{i}")
    
    with open("roster_sys_export_latest.jsonl", "w") as f:
        # Mix them up and write as jsonl with some noise
        all_records = []
        for s in valid_students:
            all_records.append({"timestamp": "2023-10-01", "student_name": s, "course_code": "AP_ENV_SCI", "status": "ENROLLED"})
        for s in dropped_students:
            all_records.append({"timestamp": "2023-09-15", "student_name": s, "course_code": "AP_ENV_SCI", "status": "DROPPED"})
        for s in other_class_students:
            all_records.append({"timestamp": "2023-10-02", "student_name": s, "course_code": random.choice(["BIO_101", "CHEM_200", "PHYS_300"]), "status": "ENROLLED"})
        
        random.shuffle(all_records)
        for record in all_records:
            # add some random garbage keys
            record["_internal_id"] = f"UID_{random.randint(1000, 9999)}"
            f.write(json.dumps(record) + "\n")

    # 2. Generate massive fragmented submission directories
    os.makedirs("submissions", exist_ok=True)
    
    formats = ['csv', 'json', 'txt']
    activities = ['ZWW-2023-FALL', 'Spring-Clean', 'Earth-Day-2022', 'NO_ID']
    
    # We will create 250 files to simulate scale.
    # Some from valid students, some from dropped, some from other classes (intruders)
    all_possible_submitters = valid_students + dropped_students + other_class_students + [f"Random_Kid_{i}" for i in range(20)]
    
    for i in range(250):
        student = random.choice(all_possible_submitters)
        fmt = random.choice(formats)
        
        # 40% chance to be the correct activity, 60% decoy
        activity = "ZWW-2023-FALL" if random.random() < 0.4 else random.choice(['Spring-Clean', 'Earth-Day-2022', 'NO_ID'])
        
        # Generate random weights
        rec_val = round(random.uniform(0.5, 15.0), 2)
        comp_val = round(random.uniform(0.1, 10.0), 2)
        land_val = round(random.uniform(1.0, 20.0), 2)
        
        # Random units
        rec_unit = random.choice(['lbs', 'kg', ''])
        comp_unit = random.choice(['lbs', 'kg', ''])
        land_unit = random.choice(['lbs', 'kg', ''])
        
        # Create nested deep path
        depth = random.randint(1, 4)
        path = "submissions"
        for d in range(depth):
            folder_name = random.choice(['week1', 'week2', 'drafts', 'final_v2', 'misc', 'late_subs', 'to_sort'])
            path = os.path.join(path, folder_name)
        os.makedirs(path, exist_ok=True)
        
        filename = os.path.join(path, f"sub_{i}_{student.lower()}.{fmt}")
        
        if fmt == 'json':
            data = {
                "metadata": {
                    "student_name": student,
                    "event_id": activity if activity != 'NO_ID' else ""
                },
                "log": {
                    "recycling": f"{rec_val} {rec_unit}".strip(),
                    "compost": f"{comp_val} {comp_unit}".strip(),
                    "landfill": f"{land_val} {land_unit}".strip()
                }
            }
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
                
        elif fmt == 'csv':
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Event", activity if activity != 'NO_ID' else ""])
                writer.writerow(["Student", student])
                writer.writerow(["Category", "Weight"])
                writer.writerow(["Recycling", f"{rec_val} {rec_unit}".strip()])
                writer.writerow(["Compost", f"{comp_val} {comp_unit}".strip()])
                writer.writerow(["Landfill", f"{land_val} {land_unit}".strip()])
                
        elif fmt == 'txt':
            with open(filename, "w") as f:
                if activity != 'NO_ID':
                    f.write(f"Activity: {activity}\n")
                f.write(f"Name: {student}\n")
                f.write("Here is my waste log:\n")
                f.write(f"- recycling: {rec_val}{rec_unit}\n")
                f.write(f"- compost: {comp_val}{comp_unit}\n")
                f.write(f"- landfill: {land_val}{comp_unit}\n") # intentional typo in unit variable for txt to add noise, but easily parsable by regex

if __name__ == "__main__":
    build_env()
