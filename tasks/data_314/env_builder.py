import os
import json
import csv

def build_env():
    base_dir = "assets/data_314"
    reports_dir = os.path.join(base_dir, "raw_reports")
    
    os.makedirs(reports_dir, exist_ok=True)

    # File 1: Valid JSON with mixed animals
    json_data = [
        {"id": "DOG-101", "species": "Dog", "county": "Cuyahoga", "status": "Injured - Broken leg", "date": "2023-11-01", "location": "Main St"},
        {"id": "CAT-772", "species": "Cat", "county": "Cuyahoga", "status": "Injured - Severe limp", "date": "2023-11-01", "location": "West 25th St"},
        {"id": "CAT-888", "species": "Cat", "county": "Cuyahoga", "status": "Healthy - Stray", "date": "2023-11-02", "location": "Public Square"}
    ]
    with open(os.path.join(reports_dir, "batch_A.json"), "w") as f:
        json.dump(json_data, f, indent=2)

    # File 2: Messy text file
    text_data = """
Animal Control Officer Notes - Oct/Nov
--------------------------------------
Record: DOG-555 | Species: Canine | County: Franklin | Cond: Healthy | Date: 2023-10-28 | Loc: Broad St
Record: FEL-091 | Species: Feline | County: Cuyahoga | Cond: Needs vet - Eye infection | Date: 2023-11-02 | Loc: Edgewater Park
Record: BIRD-01 | Species: Avian | County: Cuyahoga | Cond: Injured wing | Date: 2023-11-03 | Loc: Tremont
Record: CAT-909 | Species: Feline | County: Hamilton | Cond: Injured - Laceration | Date: 2023-11-03 | Loc: Vine St
    """
    with open(os.path.join(reports_dir, "officer_notes.txt"), "w") as f:
        f.write(text_data.strip())

    # File 3: Corrupt JSON (to test robustness)
    corrupt_json = """
    [
        {"id": "CAT-111", "species": "Cat", "county": "Cuyahoga", "status": "Injured - Tail", "date": "2023-11-04", "location": "Gordon Square"
        # missing closing braces and brackets
    """
    with open(os.path.join(reports_dir, "corrupt_data.json"), "w") as f:
        f.write(corrupt_json)

    # File 4: CSV file from another county mostly, but one valid entry
    csv_data = [
        ["RecordID", "AnimalType", "Region", "HealthCondition", "FoundDate", "FoundLocation"],
        ["RAB-01", "Rabbit", "Cuyahoga", "Healthy", "2023-11-05", "Suburbs"],
        ["CAT-222", "Cat", "Franklin", "Injured - Burn", "2023-11-05", "Downtown"],
        ["CAT-333", "Cat", "Cuyahoga", "Injured - Malnourished", "2023-11-06", "Lakewood"]
    ]
    with open(os.path.join(reports_dir, "regional_dump.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

if __name__ == "__main__":
    build_env()
