import os
import csv
import random
import shutil

def build_env():
    asset_dir = "assets/data_47"
    if os.path.exists(asset_dir):
        shutil.rmtree(asset_dir)
    os.makedirs(os.path.join(asset_dir, "attendance"), exist_ok=True)
    
    # Generate members
    members = [
        (1001, "John", "Doe"), (1002, "Jane", "Smith"), (1003, "Alice", "Johnson"),
        (1004, "Bob", "Brown"), (1005, "Charlie", "Davis"), (1006, "Eve", "Miller"),
        (1010, "Sarah", "Connor"), (1022, "Kyle", "Reese"), (1045, "Miles", "Dyson")
    ]
    # Add some dummy members
    for i in range(1050, 1070):
        members.append((i, f"First{i}", f"Last{i}"))
        
    with open(os.path.join(asset_dir, "members.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "first_name", "last_name", "email"])
        for m in members:
            writer.writerow([m[0], m[1], m[2], f"{m[1].lower()}@example.com"])
            
    # Define attendance counts
    # Target star athletes: Sarah (1010) -> 5, Kyle (1022) -> 4, Miles (1045) -> 4
    attendances = {
        "monday": [1001, 1002, 1010, 1022, 1050],
        "tuesday": [1003, 1004, 1010, 1045, 1051],
        "wednesday": [1005, 1006, 1010, 1022, 1045],
        "thursday": [1001, 1010, 1045, 1052],
        "friday": [1002, 1022, 1053],
        "saturday": [1010, 1022, 1045, 1054],
        "sunday": [1003, 1005, 1055]
    }
    
    classes = ["Spin Class", "Yoga", "Pilates", "HIIT", "Zumba"]
    
    # Generate daily logs
    for day, attendees in attendances.items():
        with open(os.path.join(asset_dir, "attendance", f"{day}.log"), "w", encoding="utf-8") as f:
            if day == "wednesday":
                # Inject corrupted lines at the beginning
                f.write("CORRUPT DATA\n")
                f.write("2023-10-11 ERROR LOG WRITE FAILURE\n")
                f.write("null | null | null\n")
                
            for member_id in attendees:
                cls = random.choice(classes)
                # Format: YYYY-MM-DD HH:MM:SS | MEMBER_ID | CLASS_NAME
                f.write(f"2023-10-10 10:00:00 | {member_id} | {cls}\n")
            
            if day == "wednesday":
                # Inject corrupted lines at the end
                f.write("0000-00-00 00:00:00 | NaN | Undefined\n")
                f.write("Fatal Exception in module Logger\n")

if __name__ == "__main__":
    build_env()
