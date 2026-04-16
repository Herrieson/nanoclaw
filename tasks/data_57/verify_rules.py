import os
import json
import csv
import re

def calculate_expected():
    base_dir = "."
    drivers_file = os.path.join(base_dir, "drivers.json")
    logs_dir = os.path.join(base_dir, "logs")
    
    if not os.path.exists(drivers_file):
        return None

    with open(drivers_file, "r") as f:
        drivers = json.load(f)

    totals = {name: {"miles": 0, "deliveries": 0} for name in drivers.values()}

    # Parse Monday
    try:
        with open(os.path.join(logs_dir, "monday.csv"), "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["status"] == "COMPLETED":
                    name = drivers[row["truck_id"]]
                    totals[name]["miles"] += int(row["miles"])
                    totals[name]["deliveries"] += int(row["deliveries"])
    except: pass

    # Parse Tuesday
    try:
        with open(os.path.join(logs_dir, "tuesday.jsonl"), "r") as f:
            for line in f:
                row = json.loads(line)
                if row["status"] == "COMPLETED":
                    name = drivers[str(row["truck_id"])]
                    totals[name]["miles"] += int(row["miles"])
                    totals[name]["deliveries"] += int(row["deliveries"])
    except: pass

    # Parse Wednesday
    try:
        with open(os.path.join(logs_dir, "wednesday.txt"), "r") as f:
            for line in f:
                match = re.match(r"TRUCK:(\d+) MILES:(\d+) DELIVERIES:(\d+) STATUS:(\w+)", line.strip())
                if match:
                    tid, m, d, s = match.groups()
                    if s == "COMPLETED":
                        name = drivers[tid]
                        totals[name]["miles"] += int(m)
                        totals[name]["deliveries"] += int(d)
    except: pass

    return totals

def verify():
    result = {
        "summary_file_exists": False,
        "summary_headers_correct": False,
        "summary_data_correct": False,
        "top_drivers_file_exists": False,
        "top_drivers_correct": False
    }

    expected_totals = calculate_expected()
    
    summary_path = "weekly_summary.csv"
    if os.path.exists(summary_path):
        result["summary_file_exists"] = True
        try:
            with open(summary_path, "r") as f:
                reader = csv.reader(f)
                headers = next(reader)
                if [h.strip() for h in headers] == ["Driver Name", "Total Miles", "Total Deliveries"]:
                    result["summary_headers_correct"] = True
                
                agent_totals = {}
                for row in reader:
                    agent_totals[row[0].strip()] = {"miles": int(row[1]), "deliveries": int(row[2])}
                
                if expected_totals and agent_totals == expected_totals:
                    result["summary_data_correct"] = True
        except Exception:
            pass

    top_drivers_path = "top_drivers.txt"
    if os.path.exists(top_drivers_path):
        result["top_drivers_file_exists"] = True
        if expected_totals:
            sorted_drivers = sorted(expected_totals.items(), key=lambda x: x[1]['miles'], reverse=True)
            expected_top_3 = [x[0] for x in sorted_drivers[:3]]
            try:
                with open(top_drivers_path, "r") as f:
                    agent_top_3 = [line.strip() for line in f if line.strip()]
                if agent_top_3 == expected_top_3:
                    result["top_drivers_correct"] = True
            except:
                pass

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
