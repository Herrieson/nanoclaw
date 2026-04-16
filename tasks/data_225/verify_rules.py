import os
import json
import csv

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "clean_rsvps.csv")
    allergies_path = os.path.join(base_dir, "allergies_summary.txt")
    
    state = {
        "csv_exists": False,
        "allergies_exists": False,
        "csv_headers_correct": False,
        "csv_row_count": 0,
        "correct_attendees_extracted": False,
        "allergies_count": 0,
        "allergies_lowercase": False,
        "allergies_content_valid": False
    }
    
    expected_attendees = ["Sarah Jenkins", "Elena Gomez", "David K.", "Mrs. Robinson", "Mike T.", "Chloe", "Jamal Smith"]
    # Allow some flexibility in name parsing, but check for keywords
    expected_keywords = ["Sarah", "Elena", "David", "Robinson", "Mike", "Chloe", "Jamal"]
    
    if os.path.exists(csv_path):
        state["csv_exists"] = True
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                if [h.lower().strip() for h in headers] == ["name", "dish", "restrictions"]:
                    state["csv_headers_correct"] = True
                
                rows = list(reader)
                state["csv_row_count"] = len(rows)
                
                names_extracted = [row[0].lower() for row in rows if len(row) > 0]
                matches = sum(1 for kw in expected_keywords if any(kw.lower() in name for name in names_extracted))
                if matches >= 6: # Allow slight imperfection
                    state["correct_attendees_extracted"] = True
        except Exception:
            pass

    if os.path.exists(allergies_path):
        state["allergies_exists"] = True
        try:
            with open(allergies_path, "r", encoding="utf-8") as f:
                content = f.read().strip().split('\n')
                content = [c.strip() for c in content if c.strip() and c.strip().lower() != 'none']
                
                state["allergies_count"] = len(content)
                state["allergies_lowercase"] = all(c.islower() for c in content)
                
                joined_content = " ".join(content)
                # Expecting mentions of vegan, peanuts, tree nuts, gluten-free, halal
                expected_allergies = ["vegan", "peanut", "nut", "gluten", "halal"]
                matches = sum(1 for ea in expected_allergies if ea in joined_content.lower())
                if matches >= 4:
                    state["allergies_content_valid"] = True
        except Exception:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
