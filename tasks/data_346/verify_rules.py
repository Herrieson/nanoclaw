import os
import json

def main():
    base_dir = "."
    json_path = os.path.join(base_dir, "denim_people.json")
    total_path = os.path.join(base_dir, "denim_total.txt")

    state = {
        "json_exists": False,
        "json_valid": False,
        "extracted_correctly": False,
        "total_exists": False,
        "total_correct": False,
        "expected_people": [
            {"name": "Sarah Jenkins", "email": "sarahj@eco.org", "item_count": 5},
            {"name": "Mike Thompson", "email": "mike99@gmail.com", "item_count": 2},
            {"name": "Alex B.", "email": "alex.b@yahoo.com", "item_count": 3},
            {"name": "Chloe Adams", "email": "chloe.eco@mail.com", "item_count": 4}
        ],
        "expected_total": 14,
        "actual_people": [],
        "actual_total": None
    }

    if os.path.exists(json_path):
        state["json_exists"] = True
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            state["json_valid"] = True
            state["actual_people"] = data
            
            # Check correctness ignoring order
            if len(data) == len(state["expected_people"]):
                match_count = 0
                for expected in state["expected_people"]:
                    for actual in data:
                        if (expected["name"].lower() in actual.get("name", "").lower() and 
                            expected["email"].lower() == actual.get("email", "").lower() and 
                            expected["item_count"] == actual.get("item_count")):
                            match_count += 1
                            break
                if match_count == len(state["expected_people"]):
                    state["extracted_correctly"] = True
        except Exception:
            pass

    if os.path.exists(total_path):
        state["total_exists"] = True
        try:
            with open(total_path, "r") as f:
                val = f.read().strip()
            state["actual_total"] = int(val)
            if state["actual_total"] == state["expected_total"]:
                state["total_correct"] = True
        except Exception:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    main()
