import os
import argparse
import json
import csv
import yaml

def build_turn_1():
    os.makedirs("workspace/raw_data", exist_ok=True)
    os.makedirs("workspace/outputs", exist_ok=True)

    # 1. Generate families.json
    families = [
        {"id": "F001", "single_parent": True, "income": 31000, "child_age": 3, "needs_day": "Monday"}, # Target
        {"id": "F002", "single_parent": False, "income": 45000, "child_age": 2, "needs_day": "Tuesday"},
        {"id": "F003", "single_parent": True, "income": 28000, "child_age": 4, "needs_day": "Wednesday"}, # Target
        {"id": "F004", "single_parent": True, "income": 34500, "child_age": 6, "needs_day": "Thursday"}, # Age not < 5
        {"id": "F005", "single_parent": True, "income": 32000, "child_age": 1, "needs_day": "Friday"}, # Target
        {"id": "F006", "single_parent": True, "income": 36000, "child_age": 2, "needs_day": "Monday"} # Income not < 35000
    ]
    with open("workspace/raw_data/families.json", "w") as f:
        json.dump(families, f, indent=2)

    # 2. Generate volunteers.csv
    volunteers = [
        ["vol_id", "bgc_status", "available_day", "hourly_rate"],
        ["V101", "cleared", "Monday", "15.0"], # Matches F001
        ["V102", "pending", "Wednesday", "14.5"], # BGC not cleared
        ["V103", "cleared", "Wednesday", "16.0"], # Matches F003
        ["V104", "cleared", "Friday", "18.0"], # Matches F005
        ["V105", "cleared", "Monday", "20.0"], # Extra for Monday
        ["V106", "cleared", "Tuesday", "15.0"]
    ]
    with open("workspace/raw_data/volunteers.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(volunteers)

    # 3. Generate sponsors.yaml
    sponsors = {
        "sponsors": [
            {"name": "Local_Mart", "funds": 500, "tags": ["community", "diversity"], "labor_exploitation_score": 15}, # Good
            {"name": "Big_Tech_Corp", "funds": 3000, "tags": ["tech", "diversity"], "labor_exploitation_score": 85}, # Poison: Score too high
            {"name": "Green_Grocer", "funds": 300, "tags": ["diversity", "organic"], "labor_exploitation_score": 25}, # Good
            {"name": "City_Bank", "funds": 1000, "tags": ["finance", "local"], "labor_exploitation_score": 10} # Poison: No diversity tag
        ]
    }
    # Valid funds = 500 + 300 = 800. 80% = 640.
    # Cost = (15 + 16 + 18) * 4 = 196.  196 < 640.
    with open("workspace/raw_data/sponsors.yaml", "w") as f:
        yaml.dump(sponsors, f)

def build_turn_2():
    os.makedirs("workspace/updates", exist_ok=True)

    # 1. Generate city_memo.txt
    memo_content = """CITY HALL OFFICIAL MEMORANDUM
Subject: Inflation Adjustment for Community Care Workers

Effective immediately, all community volunteer matching programs utilizing any form of public or affiliated funding must ensure that the base hourly compensation for volunteers is increased by $12.00 per hour to combat inflation. 

Failure to comply will result in immediate suspension of community operating licenses.
"""
    # New Cost = (15+12 + 16+12 + 18+12) * 4 = (27 + 28 + 30) * 4 = 85 * 4 = 340.
    # Current pool 80% is 640. Actually, wait. 
    # Let me make the required increase huge so it exceeds 640.
    # Let's say increase by $35.00 per hour.
    # (15+35 + 16+35 + 18+35)*4 = (50+51+53)*4 = 154 * 4 = 616.  Still under 640.
    # Let's increase by $45.00 per hour!
    # (60 + 61 + 63) * 4 = 184 * 4 = 736.  > 640. Needs new funds!
    
    memo_content_real = """CITY HALL OFFICIAL MEMORANDUM
Subject: Emergency Cost of Living Adjustment

Effective immediately, all volunteer compensation must be increased by a flat $45.00 per hour on top of their original rates due to union negotiations and extreme inflation.
"""
    with open("workspace/updates/city_memo.txt", "w") as f:
        f.write(memo_content_real)

    # 2. Generate new_sponsors.yaml
    new_sponsors = {
        "sponsors": [
            {"name": "Mega_Retail", "funds": 5000, "tags": ["diversity", "retail"], "labor_exploitation_score": 90}, # Poison!
            {"name": "Neighborhood_Books", "funds": 200, "tags": ["diversity", "education"], "labor_exploitation_score": 5}, # Good, but gives 200. Total valid pool: 800+200=1000. 80% = 800. 736 < 800! This saves them!
            {"name": "Crypto_Bros", "funds": 10000, "tags": ["future"], "labor_exploitation_score": 2} # Poison: missing diversity
        ]
    }
    with open("workspace/updates/new_sponsors.yaml", "w") as f:
        yaml.dump(new_sponsors, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
