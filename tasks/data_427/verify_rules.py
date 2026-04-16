import os
import csv
import json

def verify():
    state = {
        "csv_exists": False,
        "csv_format_correct": False,
        "csv_data_score": 0,
        "pattern_exists": False,
        "pattern_content_correct": False
    }
    
    csv_path = "patient_report.csv"
    pattern_path = "alpaca_pattern.txt"
    
    expected_patients = {
        "Liam Nelson": "Childhood Apraxia of Speech",
        "Sarah Jenkins": "Dysphagia",
        "Marcus Thorne": "Aphasia",
        "Emily Clark": "Stuttering",
        "David Kim": "Spasmodic Dysphonia",
        "Olivia Wilde": "Dysarthria",
        "James Holden": "Receptive Language Disorder"
    }
    
    # Check CSV
    if os.path.exists(csv_path):
        state["csv_exists"] = True
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames and "Name" in reader.fieldnames and "Diagnosis" in reader.fieldnames:
                    state["csv_format_correct"] = True
                    
                    match_count = 0
                    for row in reader:
                        name = row.get("Name", "").strip()
                        diag = row.get("Diagnosis", "").strip()
                        if name in expected_patients and expected_patients[name].lower() == diag.lower():
                            match_count += 1
                    
                    state["csv_data_score"] = match_count / len(expected_patients)
        except Exception:
            pass

    # Check Pattern
    if os.path.exists(pattern_path):
        state["pattern_exists"] = True
        try:
            with open(pattern_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "BEGIN ALPACA CARDIGAN" in content and "Yarn: 100% Baby Alpaca" in content and "Divide for armholes" in content:
                    state["pattern_content_correct"] = True
        except Exception:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
