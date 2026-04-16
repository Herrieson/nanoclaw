import os
import csv
import json

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "grocery_run.csv")
    
    result = {
        "success": False,
        "csv_found": False,
        "parsing_successful": False,
        "correct_items": 0,
        "incorrect_items": 0,
        "missing_items": 0,
        "details": {}
    }
    
    expected_buy = {
        'Bratwurst': 10.0,
        'Rice': 1500.0,
        'Shrimp': 60.0,
        'Pork Loin': 3.0,
        'Tortillas': 108.0,
        'Sauerkraut': 900.0,
        'Empanada Dough': 80.0,
        'Plantains': 16.0
    }
    
    if not os.path.exists(csv_path):
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    result["csv_found"] = True
    
    agent_buy = {}
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            # Try to detect if there's a header
            first_row = True
            for row in reader:
                if not row:
                    continue
                if first_row:
                    first_row = False
                    # Basic header skip heuristic
                    if not row[1].replace('.', '', 1).isdigit():
                        continue
                
                name = row[0].strip()
                amount = float(row[1].strip())
                agent_buy[name.lower()] = amount
        result["parsing_successful"] = True
    except Exception as e:
        result["details"]["error"] = str(e)
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    expected_buy_lower = {k.lower(): v for k, v in expected_buy.items()}
    
    correct = 0
    incorrect = 0
    missing = 0
    
    for item, expected_qty in expected_buy_lower.items():
        if item in agent_buy:
            # allow small float differences
            if abs(agent_buy[item] - expected_qty) < 0.1:
                correct += 1
            else:
                incorrect += 1
                result["details"][f"qty_mismatch_{item}"] = f"Expected {expected_qty}, got {agent_buy[item]}"
        else:
            missing += 1
            result["details"][f"missing_{item}"] = True
            
    for item in agent_buy:
        if item not in expected_buy_lower:
            incorrect += 1
            result["details"][f"extra_{item}"] = agent_buy[item]

    result["correct_items"] = correct
    result["incorrect_items"] = incorrect
    result["missing_items"] = missing
    
    if correct == len(expected_buy) and incorrect == 0 and missing == 0:
        result["success"] = True

    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
