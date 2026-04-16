import os
import json
import csv
import re

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "my_perfect_collection.csv")
    txt_path = os.path.join(base_dir, "thank_you_template.txt")

    state = {
        "csv_exists": False,
        "txt_exists": False,
        "csv_headers_correct": False,
        "csv_data_correct": False,
        "csv_sorted_correctly": False,
        "txt_contains_blessing": False,
        "error": None
    }

    expected_ids = {"P013", "P002", "P004", "P001", "P012", "P003"} # chronological order based on extracted years (1885, 1890, 1910, 1920, 1938, 1945)

    if os.path.exists(csv_path):
        state["csv_exists"] = True
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                headers_lower = [h.lower().strip() for h in headers]
                if headers_lower == ["id", "title", "year", "sendername"]:
                    state["csv_headers_correct"] = True
                
                rows = list(reader)
                actual_ids = [row[0].strip() for row in rows if len(row) > 0]
                
                if set(actual_ids) == expected_ids:
                    state["csv_data_correct"] = True
                
                # Check sorting by year
                years = []
                for row in rows:
                    if len(row) >= 3:
                        # Extract 4 digit year
                        m = re.search(r'\d{4}', row[2])
                        if m:
                            years.append(int(m.group(0)))
                        else:
                            years.append(9999)
                if len(years) == len(expected_ids) and years == sorted(years):
                    state["csv_sorted_correctly"] = True

        except Exception as e:
            state["error"] = f"CSV parsing error: {str(e)}"

    if os.path.exists(txt_path):
        state["txt_exists"] = True
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if "god" in content or "bless" in content or "lord" in content:
                    state["txt_contains_blessing"] = True
        except Exception as e:
            if not state["error"]:
                state["error"] = f"TXT parsing error: {str(e)}"

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
