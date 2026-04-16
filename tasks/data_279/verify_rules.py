import os
import json
import csv

def verify():
    state = {
        "literature_club_exists": False,
        "literature_club_correct": False,
        "botev_guy_exists": False,
        "botev_guy_correct": False
    }

    lit_club_path = "literature_club.csv"
    if os.path.exists(lit_club_path):
        state["literature_club_exists"] = True
        try:
            with open(lit_club_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                expected_emails = {"alice.s@gmail.com", "ivan_p@bulgaria.net", "mjane@college.edu", "sarah.lee@startup.io"}
                found_emails = set()
                for row in reader:
                    # case insensitive column names just in case
                    email_col = next((k for k in row.keys() if k and k.lower() == 'email'), None)
                    if email_col:
                        found_emails.add(row[email_col].strip())
                
                if found_emails == expected_emails:
                    state["literature_club_correct"] = True
        except Exception:
            pass

    botev_path = "botev_guy.txt"
    if os.path.exists(botev_path):
        state["botev_guy_exists"] = True
        try:
            with open(botev_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if "Ivan Petrov" in content and "45.00" in content:
                    state["botev_guy_correct"] = True
        except Exception:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
