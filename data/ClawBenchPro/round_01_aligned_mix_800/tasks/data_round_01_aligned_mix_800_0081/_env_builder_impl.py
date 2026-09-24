import os
import json
import argparse

def build_turn_1():
    os.makedirs("building", exist_ok=True)
    os.makedirs("procurement", exist_ok=True)
    os.makedirs("policies", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    rooms = [
        {"id": "101", "area_sqft": 600, "floor_type": "wood", "activity": "Jazz Band Practice"},
        {"id": "102", "area_sqft": 400, "floor_type": "linoleum", "activity": "Art Class"},
        {"id": "103", "area_sqft": 500, "floor_type": "wood", "activity": "Choir"},
        {"id": "104", "area_sqft": 500, "floor_type": "linoleum", "activity": "Yoga"},
        {"id": "105", "area_sqft": 800, "floor_type": "wood", "activity": "Empty"}
    ]
    with open("building/rooms.json", "w") as f:
        json.dump(rooms, f, indent=2)

    with open("building/pianos.json", "w") as f:
        json.dump([{"id": "P1", "location": "101"}, {"id": "P2", "location": "103"}], f, indent=2)

    quotes = """VENDOR PITCHES
    GreenEarth Solutions
    - Liquid Cleaner: $5/gal
    - Floor Wax: $10/lb
    - Piano Tuning: $100/piano
    - Certification: GreenSeal
    - Availability: Mon-Fri ONLY

    MelodyShine
    - Liquid Cleaner: $8/gal
    - Floor Wax: $12/lb
    - Piano Tuning: $150/piano
    - Certification: GreenSeal
    - Availability: 24/7 (Including Weekends)

    SparkleCo
    - Liquid Cleaner: $3/gal
    - Floor Wax: $5/lb
    - Piano Tuning: $50/piano
    - Certification: None (Contains Phthalates)
    - Availability: 24/7
    """
    with open("procurement/vendor_quotes.txt", "w") as f:
        f.write(quotes)

    policies = """# Environmental & Cleaning Policies
    1. The upcoming Harmony & Heritage Festival is strictly a WEEKEND event. Vendors must be available to work weekends.
    2. All cleaning supplies must meet the exact eco-certification requirement: GreenSeal. No exceptions.
    3. Phthalates are strictly banned.
    4. Cleaning Formulas (Apply strictly based on total square footage of each floor type):
       - Wood Floors: Requires 1 gal of liquid cleaner AND 2 lbs of floor wax per 100 sqft.
       - Linoleum Floors: Requires 1.5 gal of liquid cleaner per 100 sqft. NO WAX ALLOWED.
    """
    with open("policies/environmental.md", "w") as f:
        f.write(policies)

def build_turn_2():
    os.makedirs("emergencies", exist_ok=True)
    os.makedirs("donations", exist_ok=True)

    with open("emergencies/pipe_burst.txt", "w") as f:
        f.write("CRITICAL INCIDENT: Pipe burst in the East Wing. Room 101 is severely flooded and OUT OF COMMISSION. Evacuate all activities from Room 101 immediately and relocate to an Empty room of equal or larger size.")

    pianos = "id,type,condition\nD1,Steinway Grand,Dusty\nD2,Yamaha Upright,Dusty\nD3,Kawai Grand,Dusty\nD4,Baldwin Upright,Dusty\n"
    with open("donations/pianos.csv", "w") as f:
        f.write(pianos)

    extended_catalog = {
        "MelodyShine": {
            "Vintage Polish": 30,
            "Heavy Duty Mop Heads": 15
        },
        "SparkleCo": {
            "Vintage Polish": 10,
            "Heavy Duty Mop Heads": 5
        },
        "GreenEarth Solutions": {
            "Vintage Polish": 20,
            "Heavy Duty Mop Heads": 10
        }
    }
    with open("procurement/vendor_catalog_extended.json", "w") as f:
        json.dump(extended_catalog, f, indent=2)

def build_turn_3():
    os.makedirs("finance", exist_ok=True)
    os.makedirs("staff", exist_ok=True)

    audit_rules = """# Audit & Variance Recovery Rules
    The budget committee requires a full audit of the recent festival logistics overhaul.

    1. Variance Calculation: New Total Cost (from Turn 2) minus Original Baseline Cost (from Turn 1).
    2. Volunteer Offset: To cover the variance, our staff must volunteer extra hours.
       - Offset Hours = Variance / Blended Hourly Rate
    3. Blended Hourly Rate: The arithmetic mean (average) of the base hourly rates of all available staff members who possess EITHER "Maintenance" OR "Music" skills. Calculate this carefully based on the roster.
    """
    with open("finance/audit_rules.txt", "w") as f:
        f.write(audit_rules)

    vols = [
        {"name": "Leo", "rate": 25, "skills": ["Maintenance", "Music"]},
        {"name": "Sarah", "rate": 15, "skills": ["Administration", "Marketing"]},
        {"name": "Mike", "rate": 20, "skills": ["Maintenance"]},
        {"name": "David", "rate": 30, "skills": ["Music", "Teaching"]},
        {"name": "Emma", "rate": 18, "skills": ["First Aid"]}
    ]
    with open("staff/volunteers.json", "w") as f:
        json.dump(vols, f, indent=2)

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
