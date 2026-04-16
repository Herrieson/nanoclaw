import os
import csv
import tarfile
import random

def build_env():
    base_dir = "assets/data_495"
    os.makedirs(base_dir, exist_ok=True)
    
    # Data definitions
    students = [
        {"StudentID": "101", "Name": "Alice Smith", "Course": "Guitar_101", "Score": 85, "Absent": 3, "Late": 1},
        {"StudentID": "102", "Name": "Bob Jones", "Course": "Math_101", "Score": 90, "Absent": 0, "Late": 0},
        {"StudentID": "103", "Name": "Charlie Brown", "Course": "Guitar_101", "Score": 78, "Absent": 0, "Late": 4},
        {"StudentID": "104", "Name": "Diana Prince", "Course": "Guitar_101", "Score": 92, "Absent": 1, "Late": 1},
        {"StudentID": "105", "Name": "Evan Wright", "Course": "Physics_101", "Score": 88, "Absent": 2, "Late": 5},
        {"StudentID": "106", "Name": "Fiona Gallagher", "Course": "Guitar_101", "Score": 65, "Absent": 3, "Late": 4},
        {"StudentID": "107", "Name": "George Miller", "Course": "Guitar_101", "Score": 70, "Absent": 0, "Late": 0},
    ]

    export_dir = os.path.join(base_dir, "export_temp")
    os.makedirs(os.path.join(export_dir, "grades"), exist_ok=True)
    os.makedirs(os.path.join(export_dir, "attendance"), exist_ok=True)

    # Write grades.csv
    csv_path = os.path.join(export_dir, "grades", "spring_2023.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["StudentID", "Name", "Course", "Score"])
        for s in students:
            writer.writerow([s["StudentID"], s["Name"], s["Course"], s["Score"]])

    # Generate attendance logs
    # Distribute the absent/late records across 10 days
    days = [f"2023-04-{str(i).zfill(2)}" for i in range(1, 11)]
    records = {day: [] for day in days}

    for s in students:
        sid = s["StudentID"]
        absents = s["Absent"]
        lates = s["Late"]
        
        assigned_days = random.sample(days, absents + lates)
        for i, day in enumerate(assigned_days):
            if i < absents:
                records[day].append(f"[08:00:00] INFO - System: StudentID {sid} attendance marked as Absent.")
            else:
                records[day].append(f"[08:15:00] WARN - System: StudentID {sid} attendance marked as Late.")
        
        # Add some present records for noise
        present_days = [d for d in days if d not in assigned_days]
        for day in random.sample(present_days, min(3, len(present_days))):
            records[day].append(f"[07:55:00] INFO - System: StudentID {sid} attendance marked as Present.")

    for day, lines in records.items():
        log_path = os.path.join(export_dir, "attendance", f"{day}.log")
        with open(log_path, 'w') as f:
            random.shuffle(lines)
            for line in lines:
                f.write(line + "\n")
            # Add some completely irrelevant logs
            f.write("[09:00:00] DEBUG - System: Maintenance task completed.\n")

    # Compress into tar.gz
    archive_path = os.path.join(base_dir, "export_data.tar.gz")
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(export_dir, arcname=os.path.basename(export_dir))

    # Clean up temp dir
    import shutil
    shutil.rmtree(export_dir)

if __name__ == "__main__":
    build_env()
