import os
import json
import csv

def verify():
    result = {
        "decision_file_exists": False,
        "correct_headers": False,
        "plumbing_correct": False,
        "electrical_correct": False,
        "framing_correct": False,
    }
    
    file_path = "decision.csv"
    if os.path.exists(file_path):
        result["decision_file_exists"] = True
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) > 0:
                    headers = [h.strip() for h in rows[0]]
                    if headers == ["Trade", "Company", "Cost"]:
                        result["correct_headers"] = True
                
                for row in rows[1:]:
                    if len(row) >= 3:
                        trade, company, cost = [str(x).strip() for x in row[:3]]
                        if trade.lower() == "plumbing" and company == "Mario Bros" and str(cost) == "11500":
                            result["plumbing_correct"] = True
                        if trade.lower() == "electrical" and company == "Volt Boys" and str(cost) == "14500":
                            result["electrical_correct"] = True
                        if trade.lower() == "framing" and company == "Marcos Fuertes" and str(cost) == "18000":
                            result["framing_correct"] = True
        except Exception as e:
            result["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
