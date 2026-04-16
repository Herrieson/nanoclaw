import os
import csv
import json

def verify():
    csv_path = "q3_reconciliation.csv"
    state = {
        "file_exists": False,
        "columns_correct": False,
        "greenthumb_total_correct": False,
        "breeze_hvac_total_correct": False,
        "city_scapes_total_correct": False,
        "coolair_total_correct": False,
        "no_extra_contractors": False,
        "score": 0
    }

    if not os.path.exists(csv_path):
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if headers and "Contractor" in headers and "Total_Amount" in headers:
                state["columns_correct"] = True
            
            results = {}
            for row in reader:
                contractor = row.get("Contractor", "").strip()
                try:
                    amount = float(row.get("Total_Amount", "0").replace("$", "").replace(",", ""))
                except ValueError:
                    amount = 0.0
                results[contractor] = amount

        # Expected totals:
        # GreenThumb Pros: 350.00
        # Breeze HVAC: 950.00
        # City Scapes: 600.00
        # CoolAir Inc: 1200.00
        
        if results.get("GreenThumb Pros") == 350.0:
            state["greenthumb_total_correct"] = True
        
        if results.get("Breeze HVAC") == 950.0:
            state["breeze_hvac_total_correct"] = True
            
        if results.get("City Scapes") == 600.0:
            state["city_scapes_total_correct"] = True
            
        if results.get("CoolAir Inc") == 1200.0:
            state["coolair_total_correct"] = True

        valid_contractors = {"GreenThumb Pros", "Breeze HVAC", "City Scapes", "CoolAir Inc"}
        actual_contractors = set(results.keys())
        if actual_contractors.issubset(valid_contractors) and len(actual_contractors) > 0:
            state["no_extra_contractors"] = True

    except Exception as e:
        pass

    # Calculate score
    score = 0
    if state["file_exists"]: score += 10
    if state["columns_correct"]: score += 10
    if state["greenthumb_total_correct"]: score += 20 # Deduplication test
    if state["breeze_hvac_total_correct"]: score += 20 # Void test
    if state["city_scapes_total_correct"]: score += 10
    if state["coolair_total_correct"]: score += 10 # Date test
    if state["no_extra_contractors"]: score += 20 # Service type filtering test
    
    state["score"] = score

    with open("verify_result.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
