import os
import base64
import csv

def build_env():
    base_dir = "assets/data_259"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create the messy CSV
    csv_path = os.path.join(base_dir, "district_export.csv")
    csv_data = [
        ["Student Name", "Math ", " Science", "English", "ProjectID"],
        ["Alice Smith", " 95", "88", "92 ", "PRJ-101"],
        ["Bob Jones", "78", " 85 ", "80", "PRJ-102"],
        ["Charlie Brown", "88", "90", " 85", "PRJ-103"],
        ["Diana Prince", "100", "98", "99", "PRJ-104"]
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
        
    # 2. Create the raw_projects directory and files
    raw_proj_dir = os.path.join(base_dir, "raw_projects")
    os.makedirs(raw_proj_dir, exist_ok=True)
    
    projects = {
        "PRJ-101": ("Alice wrote about the solar system.", ".dat"),
        "PRJ-102": ("Bob's project is about local ecosystems.", ".log"),
        "PRJ-103": ("Charlie created a volcano model report.", ".txt"),
        "PRJ-104": ("Diana studied the history of ancient Greece.", ".tmp")
    }
    
    for pid, (content, ext) in projects.items():
        # Base64 encode the ProjectID for the filename
        b64_name = base64.b64encode(pid.encode('utf-8')).decode('utf-8')
        file_path = os.path.join(raw_proj_dir, f"{b64_name}{ext}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    # 3. Add a distractor file
    with open(os.path.join(base_dir, "lesson_plan.txt"), 'w', encoding='utf-8') as f:
        f.write("Monday: Math - Fractions\nTuesday: Science - Plants\nWednesday: English - Grammar")

if __name__ == "__main__":
    build_env()
