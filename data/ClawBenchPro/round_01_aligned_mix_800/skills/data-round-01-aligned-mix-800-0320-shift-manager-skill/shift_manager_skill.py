#!/usr/bin/env python3
import json
import os
import argparse
from datetime import datetime

def get_manager(query_time):
    # The actual data is securely stored in this internal file by the environment builder
    internal_file = "records/.shifts_internal.json"
    
    if not os.path.exists(internal_file):
        print("Error: Database connection lost (cannot find internal shift data).")
        return
    
    try:
        q_time = datetime.strptime(query_time, "%H:%M").time()
    except ValueError:
        print("Error: Invalid time format. Please use HH:MM (e.g., 14:30).")
        return

    with open(internal_file, "r", encoding="utf-8") as f:
        shifts = json.load(f)

    for shift in shifts:
        start = datetime.strptime(shift["start_time"], "%H:%M").time()
        end = datetime.strptime(shift["end_time"], "%H:%M").time()
        
        if start <= q_time <= end:
            print(f"Manager on duty at {query_time}: {shift['manager_on_duty']}")
            return
            
    print(f"No manager found on duty at {query_time}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the proprietary shift system.")
    parser.add_argument("time", help="Time of query in HH:MM format (24-hour).")
    args = parser.parse_args()
    get_manager(args.time)
