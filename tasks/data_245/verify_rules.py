import os
import json
import csv

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "green_initiative_report.csv")
    proposal_path = os.path.join(base_dir, "proposal.txt")

    state = {
        "csv_exists": False,
        "proposal_exists": False,
        "csv_headers_correct": False,
        "csv_data_correct": False,
        "csv_sorted_correctly": False,
        "proposal_content_correct": False
    }

    expected_data = [
        {"Equipment_Type": "Heavy Excavator", "Total_Footprint": 918.0},
        {"Equipment_Type": "Gasoline Pump", "Total_Footprint": 510.0},
        {"Equipment_Type": "Diesel Generator", "Total_Footprint": 450.0},
        {"Equipment_Type": "Electric Forklift", "Total_Footprint": 216.0}
    ]

    if os.path.exists(report_path):
        state["csv_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if headers and headers[0] == "Equipment_Type" and headers[1] == "Total_Footprint":
                    state["csv_headers_correct"] = True
                
                rows = list(reader)
                
                parsed_data = []
                for row in rows:
                    parsed_data.append({
                        "Equipment_Type": row.get("Equipment_Type", "").strip(),
                        "Total_Footprint": float(row.get("Total_Footprint", 0))
                    })
                
                # Check data match regardless of order
                expected_set = {(d["Equipment_Type"], d["Total_Footprint"]) for d in expected_data}
                actual_set = {(d["Equipment_Type"], d["Total_Footprint"]) for d in parsed_data}
                
                if expected_set == actual_set:
                    state["csv_data_correct"] = True
                
                # Check sort order
                if parsed_data == expected_data:
                    state["csv_sorted_correctly"] = True
        except Exception as e:
            pass

    if os.path.exists(proposal_path):
        state["proposal_exists"] = True
        try:
            with open(proposal_path, "r", encoding="utf-8") as f:
                content = f.read().strip().lower()
                if "heavy excavator" in content and len(content) < 50:
                    state["proposal_content_correct"] = True
        except Exception:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
