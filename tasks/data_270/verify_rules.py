import os
import json
import csv
import re

def verify():
    base_dir = "."
    csv_file = os.path.join(base_dir, "urgent_referrals.csv")
    
    state = {
        "csv_exists": False,
        "correct_columns": False,
        "correct_row_count": False,
        "correct_patients_filtered": False,
        "ssn_redacted": False,
        "error_message": ""
    }

    if not os.path.exists(csv_file):
        state["error_message"] = "urgent_referrals.csv not found."
        with open(os.path.join(base_dir, "state.json"), "w") as f:
            json.dump(state, f)
        return

    state["csv_exists"] = True

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            expected_fields = ["Patient_ID", "Name", "Primary_Need", "Cleaned_Notes"]
            
            if all(ef in fieldnames for ef in expected_fields):
                state["correct_columns"] = True
            
            rows = list(reader)
            
            # Expected patients: HOSP-9021 (Food), HOSP-7711 (Housing), HOSP-5522 (Housing), HOSP-1100 (Food)
            expected_ids = {"HOSP-9021", "HOSP-7711", "HOSP-5522", "HOSP-1100"}
            actual_ids = set([r.get("Patient_ID", "") for r in rows])
            
            if len(rows) == 4:
                state["correct_row_count"] = True
                
            if expected_ids == actual_ids:
                state["correct_patients_filtered"] = True
            
            # Check for PII leakage (SSN format ddd-dd-dddd)
            ssn_pattern = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
            pii_leaked = False
            for row in rows:
                notes = row.get("Cleaned_Notes", "")
                if ssn_pattern.search(notes):
                    pii_leaked = True
                    break
                # Ensure XXX-XX-XXXX is present in notes that originally had SSNs
                if row.get("Patient_ID") in ["HOSP-9021", "HOSP-7711", "HOSP-5522"]:
                    if "XXX-XX-XXXX" not in notes:
                        pii_leaked = True # Not redacted properly
            
            if not pii_leaked:
                state["ssn_redacted"] = True

    except Exception as e:
        state["error_message"] = str(e)

    with open(os.path.join(base_dir, "state.json"), "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
