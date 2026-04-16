import os
import json
import csv

def main():
    base_dir = "."
    csv_path = os.path.join(base_dir, "final_schedule.csv")
    
    state = {
        "csv_exists": False,
        "has_correct_headers": False,
        "is_sorted": False,
        "correct_entries": 0,
        "carlos_correct": False,
        "luis_correct": False,
        "rodriguez_correct": False,
        "diego_correct": False,
        "total_expected_entries": 4
    }

    if not os.path.exists(csv_path):
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    state["csv_exists"] = True

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            headers = [h.strip().lower() for h in headers]
            
            if headers == ["time", "name", "service", "price"]:
                state["has_correct_headers"] = True
            
            rows = list(reader)
            
            # Check sorting by time
            times = [row[0].strip() for row in rows if len(row) > 0]
            if times == sorted(times) and len(times) == 4:
                state["is_sorted"] = True

            for row in rows:
                if len(row) < 4: continue
                time, name, service, price = [x.strip() for x in row]
                
                # Normalize price to float
                try:
                    p = float(price.replace('$', ''))
                except:
                    p = -1.0

                name_lower = name.lower()
                if "carlos" in name_lower and time == "14:00" and "trim" in service.lower() and p == 10.0:
                    state["carlos_correct"] = True
                    state["correct_entries"] += 1
                elif "luis" in name_lower and time == "15:30" and "fade" in service.lower() and p == 25.0:
                    state["luis_correct"] = True
                    state["correct_entries"] += 1
                elif "rodriguez" in name_lower and time == "13:00" and "buzzcut" in service.lower() and p == 7.5:
                    state["rodriguez_correct"] = True
                    state["correct_entries"] += 1
                elif "diego" in name_lower and time == "16:00" and "fade" in service.lower() and p == 25.0:
                    state["diego_correct"] = True
                    state["correct_entries"] += 1

    except Exception as e:
        pass # Handle malformed CSVs silently and just output state

    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    main()
