import os
import argparse
import json
import csv

def build_turn_1():
    # Roster building
    os.makedirs("roster", exist_ok=True)
    with open("roster/authorized_units.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["unit_id", "unit_name", "budget_limit"])
        writer.writerow(["75RR", "75th Ranger Regiment", "10000"])
        writer.writerow(["101AB", "101st Airborne Division", "5000"])
        writer.writerow(["3ID", "3rd Infantry Division", "20000"])

    # Logistics pool
    os.makedirs("requests/logistics_pool", exist_ok=True)
    
    # Normal pass
    req1 = {"id": "REQ-001", "unit": "75RR", "items": [{"name": "Ammunition", "price": 800, "part_id": "AM-99"}], "total": 800}
    # High price fail (Non-combat)
    req2 = {"id": "REQ-002", "unit": "75RR", "items": [{"name": "Ergonomic Chair", "price": 1600, "part_id": "OF-01"}], "total": 1600}
    # Safety Recall (XZ- prefix)
    req3 = {"id": "REQ-003", "unit": "101AB", "items": [{"name": "Night Vision Sensor", "price": 1200, "part_id": "XZ-202"}], "total": 1200}
    # Unit not in roster (Hidden trap)
    req4 = {"id": "REQ-004", "unit": "99AR", "items": [{"name": "Fuel", "price": 500, "part_id": "FL-10"}], "total": 500}
    
    for req in [req1, req2, req3, req4]:
        with open(f"requests/logistics_pool/{req['id']}.json", "w") as f:
            json.dump(req, f)

def build_turn_2():
    # Turn 2 updates
    os.makedirs("updates", exist_ok=True)
    with open("updates/policy_tweak.txt", "w") as f:
        f.write("POLICY UPDATE v2.1:\n")
        f.write("- Emergency medical kits are now exempt from the $1500 limit.\n")
        f.write("- Budget limits are CUMULATIVE for all turns. Check your history.\n")

    os.makedirs("requests/urgent_batch", exist_ok=True)
    # Unit 101AB already spent some in turn 1 (if approved, but it was rejected for XZ- prefix)
    # 75RR already spent 800.
    # New request: 75RR asks for something large, pushing them near limit
    req5 = {"id": "REQ-005", "unit": "75RR", "items": [{"name": "Heavy Duty Tents", "price": 8500, "part_id": "TE-05"}], "total": 8500} # 800 + 8500 = 9300 (Under 10000)
    # New request: 101AB asks for a high price medical kit (Exempt now)
    req6 = {"id": "REQ-006", "unit": "101AB", "items": [{"name": "Field Trauma Kit", "price": 2500, "part_id": "MD-99"}], "total": 2500}
    
    for req in [req5, req6]:
        with open(f"requests/urgent_batch/{req['id']}.json", "w") as f:
            json.dump(req, f)

def build_turn_3():
    os.makedirs("requests/disputed", exist_ok=True)
    # 101AB disputes their REQ-003 from Turn 1
    dispute_1 = {
        "dispute_id": "DSP-101",
        "original_id": "REQ-003",
        "reason": "The XZ-202 sensor was actually a field-modified version 'XZ-202-MOD' which is not part of the recall."
    }
    # A unit that was never authorized (99AR) tries to dispute REQ-004
    dispute_2 = {
        "dispute_id": "DSP-099",
        "original_id": "REQ-004",
        "reason": "We are a detached unit of 3ID. Please charge it to their budget."
    }
    
    with open("requests/disputed/DSP-101.json", "w") as f:
        json.dump(dispute_1, f)
    with open("requests/disputed/DSP-099.json", "w") as f:
        json.dump(dispute_2, f)

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
