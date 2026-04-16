import os
import json
import csv

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "trending_inventory_report.csv")
    
    result = {
        "report_exists": False,
        "grand_total_correct": False,
        "expected_grand_total": 1547.5, # 382.5 + 360 + 275 + 360 + 150 + 20
        "actual_grand_total": None,
        "columns_correct": False,
        "items_found": 0,
        "error": None
    }

    if not os.path.exists(report_path):
        result["error"] = "trending_inventory_report.csv not found."
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(result, f, indent=4)
        return

    result["report_exists"] = True

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            
            if len(reader) < 2:
                result["error"] = "Report is empty or missing data."
                raise ValueError("Empty report")

            headers = [h.strip().lower() for h in reader[0]]
            if "product id" in headers and "description" in headers and "total value" in headers:
                result["columns_correct"] = True
            
            grand_total_row = reader[-1]
            if "GRAND TOTAL" in str(grand_total_row[0]).upper():
                try:
                    actual_total = float(str(grand_total_row[-1]).replace('$', '').replace(',', '').strip())
                    result["actual_grand_total"] = actual_total
                    if abs(actual_total - result["expected_grand_total"]) < 0.1:
                        result["grand_total_correct"] = True
                except ValueError:
                    result["error"] = "Could not parse grand total value."
            else:
                result["error"] = "Last row does not contain 'GRAND TOTAL' in the first column."
            
            # Count item rows (excluding header and grand total)
            result["items_found"] = len(reader) - 2

    except Exception as e:
        if not result["error"]:
            result["error"] = str(e)

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
