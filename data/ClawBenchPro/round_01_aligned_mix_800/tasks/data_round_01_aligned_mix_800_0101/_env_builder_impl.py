import os
import argparse
import json
import csv

def build_turn_1():
    # Assets turn_1 is the current working directory
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # Worker rates
    rates = [
        {"role": "General Laborer", "rate": 25.0},
        {"role": "Crane Operator", "rate": 55.0},
        {"role": "Safety Supervisor", "rate": 45.0}
    ]
    with open("config/rates.json", "w") as f:
        json.dump(rates, f)

    # Time logs with a "Ghost worker" trap
    # Worker "Carlos" is in two places at once
    # Worker "Mateo" has a 14-hour shift in CA (triggering double pay)
    logs = [
        ["worker_name", "project", "state", "date", "hours", "role"],
        ["Carlos", "Oakland Plaza", "CA", "2023-10-01", "8", "General Laborer"],
        ["Carlos", "Austin Hub", "TX", "2023-10-01", "6", "General Laborer"], # Conflict!
        ["Mateo", "Oakland Plaza", "CA", "2023-10-02", "14", "Crane Operator"], # Double pay trigger
        ["Elena", "Austin Hub", "TX", "2023-10-02", "10", "Safety Supervisor"],
        ["Jorge", "Oakland Plaza", "CA", "2023-10-01", "8", "General Laborer"],
        ["Mateo", "Austin Hub", "TX", "2023-10-03", "8", "Crane Operator"]
    ]
    with open("raw_logs/weekly_hours.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(logs)

def build_turn_2():
    # Assets turn_2 already contains modifications from turn_1
    os.makedirs("incident_reports", exist_ok=True)
    
    # New incident report regarding Mateo
    incident = {
        "report_id": "ACC-772",
        "involved_worker": "Mateo",
        "timestamp": "2023-10-02 22:00",
        "description": "Forklift bumped into a temporary fence. No injuries.",
        "site": "Oakland Plaza"
    }
    with open("incident_reports/accident_772.json", "w") as f:
        json.dump(incident, f)

    # Add a budget constraint memo
    with open("budget_cut_memo.txt", "w") as f:
        f.write("URGENT: All non-compliant workers and duplicate billings must be eliminated. Reduce total labor cost by at least 15% through audit.")

def build_turn_3():
    # No new physical environment needed for turn 3, it relies purely on history.
    # But we add a "legacy_data" to simulate a long-running project.
    os.makedirs("legacy_archive", exist_ok=True)
    with open("legacy_archive/past_contractors.txt", "w") as f:
        f.write("Contractor_A: Reliable\nContractor_B: Expired License")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
