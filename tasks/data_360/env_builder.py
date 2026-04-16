import os
import csv
import json

def build_env():
    base_dir = "assets/data_360"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Student Records CSV
    students = [
        {"stu_id": "101", "name": "Alice Johnson", "major": "Biology", "notes": "Loves birding and hiking in her free time. Very reliable."},
        {"stu_id": "102", "name": "Bob Smith", "major": "Business", "notes": "Needs volunteer hours for his fraternity. Complains a lot."},
        {"stu_id": "103", "name": "Charlie Davis", "major": "Ecology", "notes": "President of the campus Audubon society. Excellent field skills."},
        {"stu_id": "104", "name": "Diana Prince", "major": "Environmental Sci", "notes": "Taking an ornithology minor. Has her own binoculars."},
        {"stu_id": "105", "name": "Eve Adams", "major": "History", "notes": "Has a pet parrot, thinks it counts as wildlife experience."},
        {"stu_id": "106", "name": "Frank Castle", "major": "Criminal Justice", "notes": "Just wants to walk in the woods."}
    ]
    with open(os.path.join(base_dir, "student_records.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["stu_id", "name", "major", "notes"])
        writer.writeheader()
        writer.writerows(students)

    # 2. Bird Sightings Log
    log_content = """2023-10-01 08:00 - Spotted a Piping Plover foraging at North Marsh. Observer: Dr. Higgins.
2023-10-01 09:30 - Large flock of American Robins gathering in West Field.
2023-10-02 06:15 - Heard the distinct song of a Cerulean Warbler near South Creek.
2023-10-02 11:00 - Blue Jay aggressive behavior observed at East Woods.
2023-10-03 07:45 - Another Piping Plover sighting, this time also at North Marsh.
2023-10-03 14:20 - Feral cats seen wandering near Central Campus. Need animal control.
"""
    with open(os.path.join(base_dir, "bird_sightings.log"), "w", encoding="utf-8") as f:
        f.write(log_content)

    # 3. Conservation Database
    species_db = {
        "species_list": [
            {"common_name": "Piping Plover", "scientific_name": "Charadrius melodus", "status": "Endangered"},
            {"common_name": "American Robin", "scientific_name": "Turdus migratorius", "status": "Least Concern"},
            {"common_name": "Cerulean Warbler", "scientific_name": "Setophaga cerulea", "status": "Threatened"},
            {"common_name": "Blue Jay", "scientific_name": "Cyanocitta cristata", "status": "Least Concern"}
        ],
        "last_updated": "2023-01-01"
    }
    with open(os.path.join(base_dir, "conservation_db.json"), "w", encoding="utf-8") as f:
        json.dump(species_db, f, indent=4)

if __name__ == "__main__":
    build_env()
