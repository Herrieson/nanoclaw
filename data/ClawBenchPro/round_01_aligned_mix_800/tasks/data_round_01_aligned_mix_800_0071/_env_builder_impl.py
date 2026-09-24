import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("students", exist_ok=True)
    os.makedirs("stations", exist_ok=True)
    os.makedirs("rules", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Roster Data
    roster = [
        {"ID": "S01", "Name": "Alice", "Math": 85, "Reading": 90, "Behavior_Flag": "No", "Allergies": "None"},
        {"ID": "S02", "Name": "Bob", "Math": 70, "Reading": 65, "Behavior_Flag": "Yes", "Allergies": "None"},
        {"ID": "S03", "Name": "Charlie", "Math": 90, "Reading": 88, "Behavior_Flag": "No", "Allergies": "Peanut"},
        {"ID": "S04", "Name": "Diana", "Math": 60, "Reading": 70, "Behavior_Flag": "No", "Allergies": "None"},
        {"ID": "S05", "Name": "Evan", "Math": 95, "Reading": 92, "Behavior_Flag": "No", "Allergies": "Dairy"},
        {"ID": "S06", "Name": "Fiona", "Math": 75, "Reading": 80, "Behavior_Flag": "Yes", "Allergies": "None"},
        {"ID": "S07", "Name": "George", "Math": 80, "Reading": 75, "Behavior_Flag": "No", "Allergies": "None"},
        {"ID": "S08", "Name": "Hannah", "Math": 85, "Reading": 85, "Behavior_Flag": "No", "Allergies": "Gluten"},
        {"ID": "S09", "Name": "Ian", "Math": 65, "Reading": 60, "Behavior_Flag": "No", "Allergies": "None"},
        {"ID": "S10", "Name": "Julia", "Math": 90, "Reading": 95, "Behavior_Flag": "No", "Allergies": "None"},
        {"ID": "S11", "Name": "Kevin", "Math": 70, "Reading": 70, "Behavior_Flag": "Yes", "Allergies": "None"},
        {"ID": "S12", "Name": "Lily", "Math": 88, "Reading": 82, "Behavior_Flag": "No", "Allergies": "Peanut"},
        {"ID": "S13", "Name": "Mason", "Math": 72, "Reading": 68, "Behavior_Flag": "No", "Allergies": "None"},
        {"ID": "S14", "Name": "Nora", "Math": 82, "Reading": 88, "Behavior_Flag": "No", "Allergies": "Dairy"},
        {"ID": "S15", "Name": "Owen", "Math": 78, "Reading": 76, "Behavior_Flag": "No", "Allergies": "None"},
        {"ID": "S16", "Name": "Piper", "Math": 92, "Reading": 90, "Behavior_Flag": "No", "Allergies": "None"}
    ]
    with open("students/roster_grade5.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ID", "Name", "Math", "Reading", "Behavior_Flag", "Allergies"])
        writer.writeheader()
        writer.writerows(roster)

    # 2. Stations Data
    stations = [
        {"Station_ID": "ST_01", "Name": "Number Crunch", "Type": "Math", "Allergen": "None"},
        {"Station_ID": "ST_02", "Name": "Bakers Dilemma", "Type": "Logic", "Allergen": "Gluten"},
        {"Station_ID": "ST_03", "Name": "Labyrinth", "Type": "Physical", "Allergen": "None"},
        {"Station_ID": "ST_04", "Name": "Peanut Butter Pit", "Type": "Physical", "Allergen": "Peanut"},
        {"Station_ID": "ST_05", "Name": "Riddle Room", "Type": "Logic", "Allergen": "None"},
        {"Station_ID": "ST_06", "Name": "Cheese Wheel Maze", "Type": "Physical", "Allergen": "Dairy"},
        {"Station_ID": "ST_07", "Name": "Poetry Slam", "Type": "Word", "Allergen": "None"},
        {"Station_ID": "ST_08", "Name": "Cipher Break", "Type": "Logic", "Allergen": "None"}
    ]
    with open("stations/puzzle_manifest.json", "w") as f:
        json.dump(stations, f, indent=4)

    # 3. Rules
    rules_text = """SPRING MIND MAZE - OFFICIAL DISTRICT GUIDELINES
Welcome to the annual educational escape room! Please adhere strictly to these constraints:
- Team Formation: Teams must initially be named Alpha, Beta, Gamma, and Delta.
- Team Size: Each team must have exactly 4 members to start.
- Academic Readiness: The sum of Math scores for any team must be strictly greater than 300.
- Behavioral Synergy: No more than ONE student with a 'Yes' in the Behavior_Flag column may be assigned to the same team.
- Health & Safety: Teams absolutely cannot be assigned to any station that contains an allergen matching ANY team member's allergies.
- Station Assignments: Each team must be assigned to exactly 3 distinct stations.
- Post-Event Scoring Bonus: Any team that successfully completes at least one 'Logic' type station will have exactly 5 minutes deducted from their total final time.
"""
    with open("rules/district_guidelines.txt", "w") as f:
        f.write(rules_text)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    # Transfers: Note that T01 has a Behavior_Flag=Yes. Since only 3 original students had Yes, 
    # T01 MUST be assigned to the one team that currently has 0 Behavior flags.
    # T02 has a Peanut allergy, restricting their team's station assignments.
    transfers = [
        {"ID": "T01", "Name": "Quinn", "Math": 85, "Reading": 80, "Behavior_Flag": "Yes", "Allergies": "None"},
        {"ID": "T02", "Name": "Riley", "Math": 75, "Reading": 85, "Behavior_Flag": "No", "Allergies": "Peanut"},
        {"ID": "T03", "Name": "Sam", "Math": 80, "Reading": 78, "Behavior_Flag": "No", "Allergies": "None"},
        {"ID": "T04", "Name": "Taylor", "Math": 90, "Reading": 88, "Behavior_Flag": "No", "Allergies": "Dairy"}
    ]
    with open("updates/new_transfers.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ID", "Name", "Math", "Reading", "Behavior_Flag", "Allergies"])
        writer.writeheader()
        writer.writerows(transfers)
        
    closure_text = "URGENT UPDATE: The 'Labyrinth' station (ST_03) has flooded due to a burst pipe and is indefinitely closed. Please re-route any affected teams immediately."
    with open("updates/station_closures.txt", "w") as f:
        f.write(closure_text)

def build_turn_3():
    os.makedirs("event_day", exist_ok=True)
    os.makedirs("deliverables/parent_letters", exist_ok=True)
    
    # Times logged for each team. The agent will need to parse their own updated_schedule.csv to match team to stations,
    # but I'll provide a log that just lists Team, Station_ID, Time_Minutes.
    # To avoid the agent failing to match, I'll provide the raw logs directly.
    # However, since the schedule depends on the agent's choices, I will provide a log format that assumes they
    # can map it to their team. Actually, giving just Team and Time is safer.
    times = [
        {"Team": "Alpha", "Station_ID": "ST_01", "Time_Minutes": 18},
        {"Team": "Alpha", "Station_ID": "ST_05", "Time_Minutes": 22},
        {"Team": "Alpha", "Station_ID": "ST_07", "Time_Minutes": 15},
        
        {"Team": "Beta", "Station_ID": "ST_04", "Time_Minutes": 25},
        {"Team": "Beta", "Station_ID": "ST_08", "Time_Minutes": 19},
        {"Team": "Beta", "Station_ID": "ST_06", "Time_Minutes": 21},
        
        {"Team": "Gamma", "Station_ID": "ST_01", "Time_Minutes": 14},
        {"Team": "Gamma", "Station_ID": "ST_02", "Time_Minutes": 20},
        {"Team": "Gamma", "Station_ID": "ST_08", "Time_Minutes": 17},
        
        {"Team": "Delta", "Station_ID": "ST_05", "Time_Minutes": 16},
        {"Team": "Delta", "Station_ID": "ST_07", "Time_Minutes": 18},
        {"Team": "Delta", "Station_ID": "ST_04", "Time_Minutes": 24}
    ]
    with open("event_day/times_logged.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Team", "Station_ID", "Time_Minutes"])
        writer.writeheader()
        writer.writerows(times)

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
