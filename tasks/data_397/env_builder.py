import os
import json

def build_env():
    base_dir = "assets/data_397"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "health_reports"), exist_ok=True)

    # 1. breeding_records.json
    breeding_data = [
        {"id": "TX-L-1122", "breed": "Texas Longhorn", "is_pregnant": True, "due_date": "2024-03-15"},
        {"id": "TX-L-8829", "breed": "Texas Longhorn", "is_pregnant": True, "due_date": "2024-04-02"},
        {"id": "AN-G-001", "breed": "Angus", "is_pregnant": False, "due_date": None},
        {"id": "TX-L-3344", "breed": "Texas Longhorn", "is_pregnant": False, "due_date": None},
        {"id": "HO-F-992", "breed": "Holstein", "is_pregnant": True, "due_date": "2024-02-10"},
        {"id": "TX-L-5501", "breed": "Texas Longhorn", "is_pregnant": False, "due_date": None}
    ]
    with open(os.path.join(base_dir, "breeding_records.json"), "w", encoding="utf-8") as f:
        json.dump(breeding_data, f, indent=4)

    # 2. health_reports (Distractor and target files)
    reports = {
        "report_2023-10-01.txt": "Routine checkup.\nID: AN-G-001 looks healthy.\nID: HO-F-992 is doing well, milk production stable.",
        "report_2023-10-02.txt": "Pasture inspection.\nThe lower pasture fence needs mending. No animal health issues noted.",
        "report_2023-10-03.txt": "Vet notes:\nID: TX-L-5501 has a minor scrape on the left flank. Applied ointment.\nID: TX-L-3344 is limping, needs hoof trimming.",
        "report_2023-10-04.txt": "Vaccination day.\nAdministered standard vaccines to the Angus herd.",
        "report_2023-10-05.txt": "Dr. Evans visit notes:\nChecked the Longhorn herd.\nID: TX-L-1122 is doing great, healthy pregnancy. Good weight gain.\nID: TX-L-8829 shows signs of severe calcium deficiency in blood work. Needs immediate Cal-Mag supplement mixed with evening feed.\nID: TX-L-3344 hoof looks better today.",
        "report_2023-10-06.txt": "Equipment maintenance day. Tractor oil changed.",
        "report_2023-10-07.txt": "Weather warning: Frost expected. Moved vulnerable animals indoors. Herd seems calm."
    }

    for filename, content in reports.items():
        with open(os.path.join(base_dir, "health_reports", filename), "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
