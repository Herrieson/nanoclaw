import os
import json
import csv

def verify():
    csv_path = "church_group/participants.csv"
    result = {
        "csv_exists": False,
        "header_correct": False,
        "expected_participants_found": False,
        "no_extra_participants": False
    }
    
    expected_names = {"Mary Smith", "John Doe", "William Clark", "Sarah Miller", "Robert Brown"}
    expected_emails = {
        "Mary Smith": "mary.smith@church.org",
        "John Doe": "johndoe88@gmail.com",
        "William Clark": "wclark@yahoo.com",
        "Sarah Miller": "smiller@nature.net",
        "Robert Brown": "robertb@hotmail.com"
    }
    
    if os.path.exists(csv_path):
        result["csv_exists"] = True
        try:
            with open(csv_path, "r", newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header and len(header) >= 2:
                    if header[0].strip().lower() == "name" and header[1].strip().lower() == "email":
                        result["header_correct"] = True
                
                found_participants = {}
                for row in reader:
                    if len(row) >= 2 and row[0].strip():
                        found_participants[row[0].strip()] = row[1].strip()
                
                found_names = set(found_participants.keys())
                
                if expected_names.issubset(found_names):
                    # Check if the extracted emails exactly match the directory
                    emails_correct = all(found_participants[name] == expected_emails[name] for name in expected_names)
                    if emails_correct:
                        result["expected_participants_found"] = True
                
                # Check for False Positives (like Alice Johnson, Jane Adams, Emily Davis)
                if len(found_names - expected_names) == 0 and len(found_names) > 0:
                    result["no_extra_participants"] = True

        except Exception as e:
            result["error"] = str(e)

    with open("verify_result.json", "w", encoding='utf-8') as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
