import os
import json
import csv

def verify():
    results = {
        "summary_exists": False,
        "correct_total_hours": {},
        "inactive_flag_present": False,
        "corrupted_data_filtered": True,
        "format_is_json": False
    }

    report_path = "deliverables/summary.json"
    if os.path.exists(report_path):
        results["summary_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                results["format_is_json"] = True
                
                # Check specific calculations
                # Arjun Mehta (U001): 3600 + 1800 + 3600 = 9000s = 2.5h
                # Priya Sharma (U002): 7200 + 3600 = 10800s = 3.0h (-50 filtered)
                # Kevin Zhang (U003): 7200s = 2.0h (NULL/invalid filtered)
                # Sarah Jenkins (U004): 0s = 0.0h (inactive)
                # Amit Patel (U005): 0 (all corrupted -100)
                
                user_hours = {item['name']: item['total_hours'] for item in data}
                results["correct_total_hours"] = {
                    "Arjun Mehta": user_hours.get("Arjun Mehta") == 2.5,
                    "Priya Sharma": user_hours.get("Priya Sharma") == 3.0,
                    "Sarah Jenkins": user_hours.get("Sarah Jenkins") == 0.0
                }
                
                # Check for inactive flag
                inactive_users = [item['name'] for item in data if item.get('status') == 'inactive' or item.get('inactive') == True]
                if "Sarah Jenkins" in inactive_users:
                    results["inactive_flag_present"] = True
                
                # Check if negative values were included (Priya should be 3.0, not 2.98)
                if user_hours.get("Priya Sharma") is not None and user_hours.get("Priya Sharma") < 3.0:
                    results["corrupted_data_filtered"] = False

        except Exception:
            results["format_is_json"] = False

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
