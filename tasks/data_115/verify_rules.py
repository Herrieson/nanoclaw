import os
import csv
import json
import re

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "top_donors.csv")
    email_path = os.path.join(base_dir, "winner_email.txt")

    state = {
        "csv_exists": False,
        "email_exists": False,
        "csv_valid": False,
        "top_donor_correct": False,
        "email_mentions_winner": False,
        "error": None
    }

    if os.path.exists(csv_path):
        state["csv_exists"] = True
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = [row for row in reader if row]
                
                # Check if header exists, but skip if it's just names
                if len(rows) > 0:
                    # Expected: Fiona 95, Hannah 60, Charlie 55, Diana 51
                    # Emma is 50 (should not be included as strictly > 50)
                    parsed_data = []
                    for row in rows:
                        name = row[0].strip().lower()
                        if name == "name": # header
                            continue
                        try:
                            score = int(row[1].strip())
                            parsed_data.append((name, score))
                        except:
                            pass
                    
                    if len(parsed_data) > 0:
                        top_name = parsed_data[0][0]
                        if "fiona" in top_name:
                            state["top_donor_correct"] = True
                        
                        # Validate the names and scores loosely
                        valid = True
                        names_found = [p[0] for p in parsed_data]
                        if "fiona" not in names_found or "hannah" not in names_found or "charlie" not in names_found or "diana" not in names_found:
                            valid = False
                        if "emma" in names_found: # Emma is 50, shouldn't be here
                            valid = False
                        
                        state["csv_valid"] = valid
        except Exception as e:
            state["error"] = str(e)

    if os.path.exists(email_path):
        state["email_exists"] = True
        with open(email_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            if "fiona" in content:
                state["email_mentions_winner"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
