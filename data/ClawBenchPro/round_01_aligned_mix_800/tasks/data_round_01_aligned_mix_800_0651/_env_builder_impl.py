import os
import csv

def build_env():
    os.makedirs("fair_logs", exist_ok=True)
    
    # Booth 1 Data
    booth1_data = [
        ["patient_id", "first_name", "last_name", "systolic", "diastolic", "consent_signed", "kits_used"],
        ["101", "Arthur", "Dent", "110", "70", "Yes", "1"],
        ["102", "Ford", "Prefect", "142", "80", "Yes", "1"],  # High Sys -> Callback
        ["103", "Zaphod", "Beeblebrox", "120", "92", "Yes", "1"],  # High Dia -> Callback
        ["104", "Trillian", "Astra", "115", "75", "No", "2"],  # No Consent -> Callback
        ["105", "Marvin", "Android", "118", "78", "Yes", "1"],
        ["106", "Slartibartfast", "Magrathea", "125", "80", "Yes", "1"]
    ]
    
    # Booth 2 Data (Contains duplicates and some new patients)
    booth2_data = [
        ["patient_id", "first_name", "last_name", "systolic", "diastolic", "consent_signed", "kits_used"],
        ["107", "Fenchurch", "Unknown", "139", "89", "Yes", "1"], # Borderline, no callback
        ["108", "Prosser", "Mr", "150", "95", "No", "1"], # High Sys, High Dia, No Consent -> Callback
        ["102", "Ford", "Prefect", "142", "80", "Yes", "1"], # DUPLICATE of 102
        ["109", "Agrajag", "Monster", "110", "70", "Yes", "2"],
        ["105", "Marvin", "Android", "118", "78", "Yes", "0"], # DUPLICATE of 105 (different kits, agent just needs to keep first/unique by ID)
        ["110", "Gargravarr", "Mind", "100", "60", "Yes", "1"]
    ]
    
    with open(os.path.join("fair_logs", "booth_1_intake.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(booth1_data)
        
    with open(os.path.join("fair_logs", "booth_2_intake.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(booth2_data)

if __name__ == "__main__":
    build_env()
