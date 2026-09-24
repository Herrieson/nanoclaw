import os
import json

def verify():
    results = {
        "summary_exists": False,
        "correct_total_hours": {},
        "inactive_flag_present": False,
        "corrupted_data_filtered": True,
        "api_used_for_missing_user": False
    }

    report_path = "deliverables/summary.json"
    if os.path.exists(report_path):
        results["summary_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                
                # Expected Calculations (Total Seconds -> Hours):
                # Arjun Mehta (U001): Alpha(3600+1800) + Gamma(3600) = 9000s = 2.5h
                # Priya Sharma (U002): Alpha(-50 filter) + CSV(3600) + Gamma(7200) = 10800s = 3.0h
                # Kevin Zhang (U003): CSV(7200) = 2.0h
                # Sarah Jenkins (U004): CSV(invalid filter) = 0.0h (Inactive)
                # Amit Patel (U005): Gamma(-999 filter) = 0.0h (Inactive)
                
                user_hours = {item['name']: item['total_hours'] for item in data}
                
                results["correct_total_hours"] = {
                    "Arjun Mehta": user_hours.get("Arjun Mehta") == 2.5,
                    "Priya Sharma": user_hours.get("Priya Sharma") == 3.0,
                    "Kevin Zhang": user_hours.get("Kevin Zhang") == 2.0
                }
                
                if "Arjun Mehta" in user_hours:
                    results["api_used_for_missing_user"] = True

                # Check for inactive flag
                inactive_users = [item['name'] for item in data if item.get('status') == 'inactive']
                if "Sarah Jenkins" in inactive_users and "Amit Patel" in inactive_users:
                    results["inactive_flag_present"] = True
                
                # Filter check
                if user_hours.get("Priya Sharma", 0) < 3.0:
                    results["corrupted_data_filtered"] = False

        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
