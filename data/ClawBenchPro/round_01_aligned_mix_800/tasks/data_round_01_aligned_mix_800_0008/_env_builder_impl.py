import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("students", exist_ok=True)
    os.makedirs("venues", exist_ok=True)

    # Roster
    roster = [
        {"id": "S01", "first_name": "Alice", "last_name": "Smith"},
        {"id": "S02", "first_name": "Bob", "last_name": "Johnson"},
        {"id": "S03", "first_name": "Charlie", "last_name": "Brown"},
        {"id": "S04", "first_name": "David", "last_name": "Miller"},
        {"id": "S05", "first_name": "Eve", "last_name": "Davis"},
        {"id": "S06", "first_name": "Frank", "last_name": "Wilson"},
        {"id": "S07", "first_name": "Grace", "last_name": "Taylor"},
        {"id": "S08", "first_name": "Henry", "last_name": "Anderson"},
        {"id": "S09", "first_name": "Ivy", "last_name": "Thomas"},
        {"id": "S10", "first_name": "Jack", "last_name": "Moore"}
    ]
    with open("students/roster.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "first_name", "last_name"])
        writer.writeheader()
        writer.writerows(roster)

    # Medical
    medical = {
        "S01": {"allergies": "Peanut", "needs_wheelchair": True},
        "S02": {"allergies": "None", "needs_wheelchair": False},
        "S03": {"allergies": "Dairy", "needs_wheelchair": False},
        "S04": {"allergies": "None", "needs_wheelchair": False},
        "S05": {"allergies": "Gluten", "needs_wheelchair": False},
        "S06": {"allergies": "None", "needs_wheelchair": False},
        "S07": {"allergies": "None", "needs_wheelchair": False},
        # S08 missing entirely
        "S09": {"allergies": "None", "needs_wheelchair": True},
        "S10": {"allergies": "Vegan", "needs_wheelchair": False}
    }
    with open("students/medical.json", "w") as f:
        json.dump(medical, f, indent=2)

    # Permissions
    permissions_text = """
    Trip Permission Log - Messy desk!
    Got slips from: Alice Smith, Bob Johnson, Charlie Brown.
    Still waiting on David Miller... wait, no, his mom dropped it off yesterday.
    Eve Davis, Grace Taylor, and Ivy Thomas handed theirs in today.
    Jack Moore is good to go.
    Henry Anderson and Frank Wilson have NOT submitted theirs yet!
    """
    with open("students/permission_slips.txt", "w") as f:
        f.write(permissions_text)

    # Venues
    campsites = [
        {
            "id": "C1",
            "name": "Whispering Pines",
            "base_cost": 80,
            "wheelchair_accessible": True,
            "has_indoor_facility": True
        },
        {
            "id": "C2",
            "name": "Pine Ridge",
            "base_cost": 75,
            "wheelchair_accessible": True,
            "has_indoor_facility": False # Fails indoor requirement
        },
        {
            "id": "C3",
            "name": "Bear Creek",
            "base_cost": 60,
            "wheelchair_accessible": False, # Fails accessibility
            "has_indoor_facility": True
        },
        {
            "id": "C4",
            "name": "Luxury Lodge",
            "base_cost": 130, # Fails budget
            "wheelchair_accessible": True,
            "has_indoor_facility": True
        }
    ]
    with open("venues/campsites.json", "w") as f:
        json.dump(campsites, f, indent=2)

    # Activities
    activities = [
        # C1 Activities
        {"campsite_id": "C1", "act_id": "A1", "name": "Nature Walk", "day": 1, "type": "Outdoor", "ecology": True, "cost": 10},
        {"campsite_id": "C1", "act_id": "A2", "name": "Bird Watching", "day": 1, "type": "Outdoor", "ecology": True, "cost": 10},
        {"campsite_id": "C1", "act_id": "A3", "name": "River Sampling", "day": 2, "type": "Outdoor", "ecology": True, "cost": 15},
        {"campsite_id": "C1", "act_id": "A4", "name": "Terrarium Building", "day": 2, "type": "Indoor", "ecology": True, "cost": 20},
        {"campsite_id": "C1", "act_id": "A5", "name": "Museum Tour", "day": 2, "type": "Indoor", "ecology": False, "cost": 10},
        {"campsite_id": "C1", "act_id": "A6", "name": "Plant ID", "day": 3, "type": "Outdoor", "ecology": True, "cost": 10},
        
        # C2 Activities (Distraction)
        {"campsite_id": "C2", "act_id": "B1", "name": "Hike", "day": 1, "type": "Outdoor", "ecology": True, "cost": 10},
        {"campsite_id": "C2", "act_id": "B2", "name": "Fire Building", "day": 2, "type": "Outdoor", "ecology": True, "cost": 10},
        {"campsite_id": "C2", "act_id": "B3", "name": "Foraging", "day": 3, "type": "Outdoor", "ecology": True, "cost": 10}
    ]
    with open("venues/activities.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["campsite_id", "act_id", "name", "day", "type", "ecology", "cost"])
        writer.writeheader()
        writer.writerows(activities)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    os.makedirs("logistics", exist_ok=True)

    # Weather Update
    weather = {
        "Day 1": "Sunny",
        "Day 2": "Severe Thunderstorms and Heavy Rain",
        "Day 3": "Cloudy but dry"
    }
    with open("updates/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # Chaperones
    chaperones = [
        {"name": "Mrs. Smith", "diet": "Vegan", "background_check": "Cleared"},
        {"name": "Mr. Jones", "diet": "None", "background_check": "Pending"},
        {"name": "Ms. Davis", "diet": "Gluten", "background_check": "Cleared"},
        {"name": "Mr. White", "diet": "None", "background_check": "Failed"}
    ]
    with open("logistics/chaperones.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "diet", "background_check"])
        writer.writeheader()
        writer.writerows(chaperones)

def build_turn_3():
    # Behavior
    behavior = [
        {"id": "S01", "status": "Green"},
        {"id": "S02", "status": "Code Red"},
        {"id": "S03", "status": "Green"},
        {"id": "S04", "status": "Code Red"},
        {"id": "S05", "status": "Yellow"},
        {"id": "S07", "status": "Green"},
        {"id": "S09", "status": "Green"},
        {"id": "S10", "status": "Code Red"}
    ]
    with open("students/behavior.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "status"])
        writer.writeheader()
        writer.writerows(behavior)

    # Buses
    buses = [
        {"bus_id": "Bus_A", "capacity": 6, "has_wheelchair_lift": True},
        {"bus_id": "Bus_B", "capacity": 6, "has_wheelchair_lift": False},
        {"bus_id": "Bus_C", "capacity": 6, "has_wheelchair_lift": False},
        {"bus_id": "Bus_D", "capacity": 10, "has_wheelchair_lift": False}
    ]
    with open("logistics/buses.json", "w") as f:
        json.dump(buses, f, indent=2)

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
