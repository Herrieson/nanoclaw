import os
import csv
import json

def verify():
    workspace = "."
    target_file = os.path.join(workspace, "unpaid_pet_fines.csv")
    
    state = {
        "file_exists": False,
        "correct_headers": False,
        "identified_violators": [],
        "extra_violators": [],
        "score": 0
    }
    
    expected_violators = {"101", "104", "106"}
    expected_fines = {"250", "$250", "250.00", "$250.00"}
    
    if not os.path.exists(target_file):
        with open(os.path.join(workspace, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            headers = [h.strip() for h in headers]
            
            if ["Unit", "Tenant Name", "Fine Amount"] == headers:
                state["correct_headers"] = True
            
            found_units = set()
            fine_values_correct = True
            
            for row in reader:
                if len(row) >= 3:
                    unit = str(row[0]).strip()
                    fine = str(row[2]).strip()
                    found_units.add(unit)
                    
                    if fine not in expected_fines:
                        fine_values_correct = False
            
            state["identified_violators"] = list(found_units.intersection(expected_violators))
            state["extra_violators"] = list(found_units - expected_violators)
            
            # Scoring logic
            score = 0
            if state["correct_headers"]:
                score += 10
            
            # 20 points per correct violator (101, 104, 106)
            score += len(state["identified_violators"]) * 20
            
            # Deduct points for false positives (people who paid, or don't have pets)
            score -= len(state["extra_violators"]) * 20
            
            # 30 points if the fine values were correctly formatted as 250
            if fine_values_correct and len(state["identified_violators"]) > 0:
                score += 30
                
            state["score"] = max(0, min(100, score))
            
    except Exception as e:
        state["error"] = str(e)
        state["score"] = 0

    with open(os.path.join(workspace, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
