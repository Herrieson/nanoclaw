import os
import csv
import json

def setup_environment():
    base_path = "assets/data_304/internal/raw_data"
    os.makedirs(base_path, exist_ok=True)

    # 1. Generate Staff Availability & Rules
    staff_info = {
        "Marcus": {"max_time": "16:00", "specialty": "General"},
        "Sarah": {"max_time": "18:00", "specialty": "Advanced Math"},
        "Riley": {"max_time": "17:00", "specialty": "General"}
    }
    with open(os.path.join(base_path, "staff_constraints.json"), "w") as f:
        json.dump(staff_info, f, indent=4)

    # 2. Generate Messy Exported Schedule (The "Disaster")
    # Columns: Time, Room, Tutor, Subject, StudentCount
    raw_data = [
        ["14:00", "Room A", "Marcus", "History", "10"],
        ["14:00", "Room B", "Sarah", "Advanced Math", "14"], # Over capacity (Room B limit 12)
        ["15:00", "Room A", "Marcus", "English", "8"],
        ["15:00", "Room C", "Marcus", "History", "5"],     # CONFLICT: Marcus in two rooms + Room C is Math only
        ["16:30", "Room B", "Marcus", "Biology", "10"],    # VIOLATION: Marcus works after 16:00
        ["16:00", "Room C", "Sarah", "Advanced Math", "20"], # OK (Room C Math only)
        ["15:00", "Room B", "Riley", "Art", "13"],         # Over capacity (Room B limit 12)
        ["17:00", "Room A", "Sarah", "Physics", "5"],
    ]

    export_path = os.path.join(base_path, "vendor_export_raw.csv")
    with open(export_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Room", "Tutor", "Subject", "StudentCount"])
        writer.writerows(raw_data)

    # 3. Create a README with implicit clues
    with open(os.path.join(base_path, "room_specs.txt"), "w") as f:
        f.write("Room A: Capacity 20\nRoom B: Capacity 12\nRoom C: Capacity 25, Math Specialization Required.")

if __name__ == "__main__":
    setup_environment()
