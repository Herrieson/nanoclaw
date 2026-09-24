import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("requests", exist_ok=True)
    os.makedirs("staff", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)

    with open("requests/lunar_tides.json", "w") as f:
        json.dump({
            "band": "The Lunar Tides",
            "duration_hours": 5,
            "preferred_days": ["Monday", "Tuesday"],
            "preferred_start_time": "09:00"
        }, f, indent=2)

    with open("requests/neon_monks.json", "w") as f:
        json.dump({
            "band": "Neon Monks",
            "duration_hours": 4,
            "preferred_days": ["Wednesday", "Thursday"],
            "preferred_start_time": "13:00"
        }, f, indent=2)

    with open("requests/crimson_dawn.json", "w") as f:
        json.dump({
            "band": "Crimson Dawn",
            "duration_hours": 6,
            "preferred_days": ["Tuesday", "Wednesday"],
            "preferred_start_time": "09:00"
        }, f, indent=2)

    with open("staff/engineers.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Skill", "MaxHoursPerDay"])
        writer.writerow(["Dave", "Analog Mixing", "8"])
        writer.writerow(["Sarah", "Digital Mastering", "8"])
        writer.writerow(["Mike", "Vocal Tuning", "8"])

    with open("inventory/studios.json", "w") as f:
        json.dump({
            "Studio A": {
                "console": "Neve Console",
                "mic": "U87"
            },
            "Studio B": {
                "console": "SSL Console",
                "mic": "SM7B"
            }
        }, f, indent=2)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    
    with open("updates/vip_request.json", "w") as f:
        json.dump({
            "band": "Yoga Fire",
            "duration_hours": 4,
            "preferred_days": ["Wednesday"],
            "preferred_start_time": "13:00",
            "studio": "Studio A"
        }, f, indent=2)
        
    with open("updates/staff_sick.txt", "w") as f:
        f.write("Dave has the flu and will be out all day on Wednesday.\n")

def build_turn_3():
    os.makedirs("updates", exist_ok=True)
    os.makedirs("rentals", exist_ok=True)
    
    with open("updates/equipment_alert.txt", "w") as f:
        f.write("URGENT: The Neve Console in Studio A just completely died. It will be out of commission for Thursday and Friday.\n")
        
    with open("rentals/catalog.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Equipment", "CostPerDay"])
        writer.writerow(["Neve Console", "500"])
        writer.writerow(["SSL Console", "400"])
        writer.writerow(["U87 Mic", "50"])
        writer.writerow(["SM7B Mic", "30"])

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
