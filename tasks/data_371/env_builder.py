import os
import csv
import json

def build_env():
    base_dir = "assets/data_371"
    notes_dir = os.path.join(base_dir, "field_notes")
    
    os.makedirs(notes_dir, exist_ok=True)

    # File 1: CSV format
    csv_data = [
        ["Date", "Student", "Species", "Location"],
        ["2023-10-01", "Alice", "red maple", "School Yard"],
        ["2023-10-01", "Bob", "Blue Jay", "Central Park"],
        ["2023-10-02", "Alice", "Monarch Butterfly", "Community Garden"],
        ["2023-10-02", "David", "red maple", "School Yard"],
        ["2023-10-02", "Emma", "White Oak", "Forest Trail"]
    ]
    with open(os.path.join(notes_dir, "group_a.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # File 2: JSON format
    json_data = [
        {"time": "2023-10-01T10:00:00", "student_name": "Charlie", "organism": "RED MAPLE", "area": "Park"},
        {"time": "2023-10-01T11:30:00", "student_name": "David", "organism": "blue jay", "area": "River Bank"},
        {"time": "2023-10-02T09:15:00", "student_name": "Liam", "organism": "White Oak", "area": "Forest Trail"},
        {"time": "2023-10-02T14:20:00", "student_name": "Alice", "organism": "Red Maple", "area": "School Yard"}
    ]
    with open(os.path.join(notes_dir, "group_b.json"), "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)

    # File 3: Messy LOG format
    log_data = """[2023-10-01] Observer: Emma | Found: BLUE JAY | At: Park
[2023-10-02] Observer: Liam | Found: monarch butterfly | At: Garden
[2023-10-03] Observer: Noah | Found: Red maple | At: Street
[2023-10-03] Observer: Bob | Found: blue jay | At: Park
"""
    with open(os.path.join(notes_dir, "group_c.log"), "w", encoding="utf-8") as f:
        f.write(log_data)

if __name__ == "__main__":
    build_env()
