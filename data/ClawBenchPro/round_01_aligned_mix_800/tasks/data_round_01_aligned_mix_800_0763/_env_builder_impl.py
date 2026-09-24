import os
import json
import csv

def build_env():
    # Execute in the local cwd as requested. Do NOT prefix with assets/data_round_01_aligned_mix_800_0763/.
    os.makedirs("raw_data", exist_ok=True)

    # 1. Official Whitelist
    registered_volunteers = ["Sarah", "David", "Miriam", "Jamal", "Chloe", "Ezra"]
    with open("raw_data/registered_volunteers.json", "w", encoding="utf-8") as f:
        json.dump(registered_volunteers, f, indent=4)

    # 2. Messy Volunteer Log (contains uninvited people and extra spaces)
    hours_content = """
    Sarah: 4.5 hours
    Chad: 6 hours (claimed)
    David: 2.0 hours
    Karen: 3.5 hours
    Jamal: 4 hours
    Miriam: 1.5 hours
    """
    with open("raw_data/volunteer_hours.txt", "w", encoding="utf-8") as f:
        f.write(hours_content.strip())

    # 3. Donations Manifest (Mix of healthy/useful and junk)
    donations = [
        ["Item_Name", "Quantity", "Category"],
        ["Organic Apples", "50", "Food"],
        ["Candy Bars", "100", "Snacks"],
        ["Meditation Cushions", "10", "Wellness"],
        ["Soda Cans", "200", "Beverages"],
        ["Social Justice Pamphlets", "500", "Education"],
        ["Whole Wheat Bread", "20", "Food"],
        ["Processed Cheese Slices", "30", "Food"]
    ]
    with open("raw_data/donations.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(donations)

if __name__ == "__main__":
    build_env()
