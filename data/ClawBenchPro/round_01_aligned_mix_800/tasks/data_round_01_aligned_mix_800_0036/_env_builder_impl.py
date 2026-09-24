import os
import json
import csv
import argparse

def build_turn_1():
    os.makedirs("vendors/applications", exist_ok=True)
    os.makedirs("community_center", exist_ok=True)
    os.makedirs("volunteers", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Vendor 1: Tier 2, 100 sqft, 500W, no special help needed. Valid.
    with open("vendors/applications/vendor_1_vinyl.txt", "w", encoding="utf-8") as f:
        f.write("Hi, Joe's Vintage Vinyl here. We need a 10x10 space. Power required: 500W for our record players and vintage amps. All our packaging is recycled paper. We have no corporate affiliations, strictly local!")

    # Vendor 2: Corporate franchise. Rule breaker.
    with open("vendors/applications/vendor_2_toys.txt", "w", encoding="utf-8") as f:
        f.write("MegaCorp Toys applying for a booth. 15x15 space. We are a franchise of GlobalToys Inc. Need 1000W. We use standard packaging.")

    # Vendor 3: Tier 1, 25 sqft, 0W, needs Heavy Lifting during setup. Valid.
    with open("vendors/applications/vendor_3_crafts.txt", "w", encoding="utf-8") as f:
        f.write("Sally's Handknits. I just need a small 5x5 booth. No power needed at all. Eco-friendly bags used always. I'm getting older though, so I strictly need help carrying heavy boxes during setup.")

    # Vendor 4: Plastic bags and >150 sqft. Rule breaker.
    with open("vendors/applications/vendor_4_food.txt", "w", encoding="utf-8") as f:
        f.write("Big Bite Burgers. 15x15 footprint. We need 2000W for the grills. We serve everything in plastic bags. We are locally owned.")

    # Vendor 5: Tier 2, 100 sqft, 1500W, needs First Aid during event. Valid.
    with open("vendors/applications/vendor_5_bakery.txt", "w", encoding="utf-8") as f:
        f.write("Progressive Pies! 10x10 booth size. We need 1500W for our convection ovens. Completely eco-friendly compostable plates. Because we use peanut oil and have hot ovens, we absolutely need someone with First Aid on standby during the event.")

    # Vendor 6: Tier 2, 64 sqft, 200W, no special help needed. Valid.
    with open("vendors/applications/vendor_6_clothes.txt", "w", encoding="utf-8") as f:
        f.write("Retro Threads. 8x8 booth. 200W for our cool neon lighting. All eco-friendly upcycled materials. We handle our own setup.")

    rules = {
        "max_footprint_sqft": 150,
        "prohibited_keywords": ["corporate", "franchise", "plastic bags"],
        "eco_packaging_required": True
    }
    with open("community_center/rules.json", "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=4)

    roster = [
        ["Name", "Shift_Start", "Shift_End", "Certifications"],
        ["Mary", "08:00", "12:00", "Heavy Lifting"],
        ["John", "08:00", "12:00", "Heavy Lifting"],
        ["Dave", "12:00", "18:00", "First Aid"],
        ["Sue", "12:00", "18:00", "First Aid"],
        ["Bob", "08:00", "18:00", "None"]
    ]
    with open("volunteers/roster.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(roster)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    
    # Gym Zones:
    # Zone A: 200 sqft, 2000W limit.
    # Zone B: 100 sqft, 500W limit.
    # Total available: 300 sqft, 2500W.
    # Approved from Turn 1: 
    # V1 (100sqft, 500W)
    # V3 (25sqft, 0W)
    # V5 (100sqft, 1500W)
    # V6 (64sqft, 200W)
    # Total needed: 289 sqft, 2200W.
    # V5 must go to Zone A (1500W). Leaves 100sqft, 500W in A.
    # V1 can fit exactly in remaining Zone A (100sqft, 500W).
    # V6 must go to Zone B (64sqft, 200W). Leaves 36sqft, 300W in B.
    # V3 can fit in Zone B (25sqft, 0W).
    # All fit if packed optimally!
    
    gym_layout = {
        "zones": [
            {"id": "A", "max_sqft": 200, "max_power_W": 2000},
            {"id": "B", "max_sqft": 100, "max_power_W": 500}
        ]
    }
    with open("updates/gym_layout.json", "w", encoding="utf-8") as f:
        json.dump(gym_layout, f, indent=4)

    # Dave and Mary get sick. The agent must reassign to Sue and John.
    with open("updates/call_outs.txt", "w", encoding="utf-8") as f:
        f.write("Call outs for today due to the stomach bug:\n- Mary\n- Dave\n- Bob\n")

def build_turn_3():
    os.makedirs("finance", exist_ok=True)
    
    # Receipts trap: MegaCorp Toys (Vendor 2) snuck in, must be ignored.
    receipts = [
        ["Vendor_Name", "Total_Sales"],
        ["Joe's Vintage Vinyl", "1200.00"],
        ["MegaCorp Toys", "5000.00"],   # Trap
        ["Sally's Handknits", "350.00"],
        ["Progressive Pies", "800.00"],
        ["Retro Threads", "450.00"],
        ["Big Bite Burgers", "900.00"]   # Trap
    ]
    with open("finance/receipts.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(receipts)

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
