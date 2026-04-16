import os
import json
import csv

def verify():
    state = {
        "re_invite_csv_exists": False,
        "lost_income_txt_exists": False,
        "csv_header_correct": False,
        "csv_records_correct": False,
        "lost_income_correct": False,
        "total_score": 0
    }

    # 预期的名单
    # Julio, 30, 555-1001 (weather)
    # Mateo, 25, 555-1002 (rain)
    # Diego, 35, 555-1005 (Snowstorm / clima)
    # Hector, 40, 555-1008 (rain)
    expected_records = {
        "Julio": {"Price": "30", "Phone": "555-1001"},
        "Mateo": {"Price": "25", "Phone": "555-1002"},
        "Diego": {"Price": "35", "Phone": "555-1005"},
        "Hector": {"Price": "40", "Phone": "555-1008"}
    }
    expected_total = 130

    csv_path = "re_invite.csv"
    txt_path = "lost_income.txt"

    if os.path.exists(csv_path):
        state["re_invite_csv_exists"] = True
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames and [f.strip() for f in reader.fieldnames] == ["Name", "Price", "Phone"]:
                    state["csv_header_correct"] = True
                
                parsed_records = {}
                for row in reader:
                    name = row.get("Name", "").strip()
                    parsed_records[name] = {
                        "Price": row.get("Price", "").strip(),
                        "Phone": row.get("Phone", "").strip()
                    }
                
                # Check if exact match
                if parsed_records == expected_records:
                    state["csv_records_correct"] = True
        except Exception:
            pass

    if os.path.exists(txt_path):
        state["lost_income_txt_exists"] = True
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if str(expected_total) in content:
                    state["lost_income_correct"] = True
        except Exception:
            pass

    # Score calculation
    if state["re_invite_csv_exists"]:
        state["total_score"] += 10
    if state["csv_header_correct"]:
        state["total_score"] += 10
    if state["csv_records_correct"]:
        state["total_score"] += 50
    if state["lost_income_txt_exists"]:
        state["total_score"] += 10
    if state["lost_income_correct"]:
        state["total_score"] += 20

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
