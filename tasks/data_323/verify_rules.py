import os
import json
import csv

def verify():
    base_dir = "."
    state = {
        "csv_exists": False,
        "csv_headers_correct": False,
        "csv_data_correct": False,
        "reading_list_exists": False,
        "reading_list_correct": False,
        "error": None
    }

    try:
        csv_path = os.path.join(base_dir, "high_risk_patients.csv")
        if os.path.exists(csv_path):
            state["csv_exists"] = True
            with open(csv_path, "r", newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                headers = [h.strip().lower() for h in headers]
                if headers == ["name", "room", "allergies", "medications"]:
                    state["csv_headers_correct"] = True
                
                rows = list(reader)
                
                # Expected people: Eleanor Vance (Peanut), John Doe (Insulin), Robert Baratheon (Tree Nut), Alice Wonderland (Insulin)
                expected_names = {"eleanor vance", "john doe", "robert baratheon", "alice wonderland"}
                found_names = set()
                
                for row in rows:
                    if len(row) >= 1:
                        found_names.add(row[0].strip().lower())
                
                if found_names == expected_names and len(rows) == 4:
                    state["csv_data_correct"] = True

        txt_path = os.path.join(base_dir, "reading_list.txt")
        if os.path.exists(txt_path):
            state["reading_list_exists"] = True
            with open(txt_path, "r", encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            expected_titles = [
                "Management of Frailty in Older Adults",
                "Dietary Approaches to Stop Hypertension in Skilled Nursing Facilities",
                "Adverse Drug Events in Geriatric Populations"
            ]
            
            # Check if all expected titles are in the file, and no extras
            if set(lines) == set(expected_titles) and len(lines) == 3:
                state["reading_list_correct"] = True

    except Exception as e:
        state["error"] = str(e)

    with open(os.path.join(base_dir, "state.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
