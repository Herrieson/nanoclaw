import os
import json
import csv

def build_env():
    # Ensure the target directory exists in the current working directory
    work_dir = "work_files"
    os.makedirs(work_dir, exist_ok=True)

    # 1. Create current_stock.csv
    stock_path = os.path.join(work_dir, "current_stock.csv")
    with open(stock_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Part_ID", "Part_Name", "Quantity_On_Hand"])
        writer.writerow(["EV-101", "Lithium Cell Pack", "4500"])
        writer.writerow(["EV-102", "Stator Coil", "800"])
        writer.writerow(["EV-103", "Rotor Assembly", "120"])
        writer.writerow(["EV-104", "Cooling Pump", "50"])

    # 2. Create upcoming_builds.json (Needs exceed stock)
    builds_path = os.path.join(work_dir, "upcoming_builds.json")
    build_data = {
        "shift_1_requirements": {
            "EV-101": 2000,
            "EV-102": 400,
            "EV-103": 100,
            "EV-104": 20
        },
        "shift_2_requirements": {
            "EV-101": 3000,
            "EV-102": 500,
            "EV-103": 50,
            "EV-104": 40
        }
    }
    with open(builds_path, "w", encoding="utf-8") as f:
        json.dump(build_data, f, indent=4)

    # 3. Create carriers_list.txt with messy data
    carriers_path = os.path.join(work_dir, "carriers_list.txt")
    with open(carriers_path, "w", encoding="utf-8") as f:
        f.write("--- APPROVED EXPEDITE CARRIERS ---\n")
        f.write("Carrier A | Standard Delivery | $1.20/lb | Status: ACTIVE\n")
        f.write("Carrier B | Same-Day | $5.50/lb | Status: SUSPENDED (Do not use!)\n")
        f.write("Carrier C | Same-Day | $4.20/lb | Status: ACTIVE\n")
        f.write("Carrier D | Same-Day | $3.90/lb | Status: ACTIVE\n")
        f.write("Carrier E | Express | $2.50/lb | Status: ACTIVE\n")
        f.write("Note: Only use active carriers for Same-Day if lines are down.\n")

    # 4. Create distractor files (showing low conscientiousness & quirks)
    with open(os.path.join(work_dir, "vintage_jewelry_wishlist.txt"), "w", encoding="utf-8") as f:
        f.write("1. Art Deco Diamond Brooch - $450\n2. 1920s Pearl Necklace - $300\n(Must buy for anniversary!)")

    with open(os.path.join(work_dir, "asdasdasd.log"), "w", encoding="utf-8") as f:
        f.write("aklsdjflkajsdfkljasdklfj\nmy toddler mashed the keyboard")

if __name__ == "__main__":
    build_env()
