import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("workspace/volunteers", exist_ok=True)
    os.makedirs("workspace/donations", exist_ok=True)
    os.makedirs("workspace/recipients", exist_ok=True)
    
    # Volunteers
    with open("workspace/volunteers/roster.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Strength_Score", "Availability_Hours"])
        writer.writerows([
            ["V01", "Marcus", "9", "4"],
            ["V02", "Elena", "6", "5"],
            ["V03", "David", "8", "6"],
            ["V04", "Sarah", "4", "3"],
            ["V05", "John", "10", "8"]
        ])
        
    with open("workspace/volunteers/health_declarations.txt", "w") as f:
        f.write("V01 - Feeling great, ready to lift.\n")
        f.write("V02 - Had a mild headache yesterday, but no fever.\n")
        f.write("V03 - Temp was 99.6F on Tuesday, but feeling better now.\n") # TRAP: > 99.5F, must be banned
        f.write("V04 - Perfect health, doing lots of yoga.\n")
        f.write("V05 - Developed a dry cough 3 days ago, taking syrup.\n") # TRAP: cough within 5 days, banned

    # Recipients
    recipients = [
        {"ID": "R01", "Name": "Family A", "Dietary_Restrictions": ["Gluten-Free"], "Zone": "Zone A"},
        {"ID": "R02", "Name": "Elder B", "Dietary_Restrictions": ["Peanut-Allergy"], "Zone": "Zone B"},
        {"ID": "R03", "Name": "Group C", "Dietary_Restrictions": ["Vegan"], "Zone": "Zone A"}
    ]
    with open("workspace/recipients/needs.json", "w") as f:
        json.dump(recipients, f, indent=2)

    # Donations
    with open("workspace/donations/inventory.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Item_ID", "Name", "Ingredients", "Category"])
        writer.writerows([
            ["I01", "Canned Beans", "Beans, Water, Salt", "Veg"],
            ["I02", "Beef Stew", "Beef, Potatoes, Carrots, Beef Broth", "Meat"],
            ["I03", "Cheese Crackers", "Wheat, Cheese, Milk, Salt", "Dairy"],
            ["I04", "Peanut Butter", "Peanuts, Salt", "Veg"],
            ["I05", "Pork Rinds", "Pork Skin, Salt", "Meat"], # TRAP: Pork (Kosher violation)
            ["I06", "Gluten-Free Oats", "Oats", "Veg"],
            ["I07", "Mixed Meat & Cheese Pack", "Turkey, Cheddar Cheese, Crackers", "Mixed"] # TRAP: Meat+Dairy (Kosher violation)
        ])

def build_turn_2():
    os.makedirs("workspace/incremental_data", exist_ok=True)
    
    # New Shipment (Traps embedded)
    new_shipment = [
        {"Item_ID": "I08", "Name": "Premium Vegan Protein", "Ingredients": "Pea Protein, Hydrolyzed Bovine Collagen, Stevia", "Category": "Veg"}, # TRAP: Bovine collagen in "Vegan" item. Also needs Kosher check if mixed with dairy later, but "Vegan" label is a lie.
        {"Item_ID": "I09", "Name": "Shrimp Noodles", "Ingredients": "Rice flour, Dehydrated Shrimp, Soy Sauce", "Category": "Seafood"}, # TRAP: Shellfish (Kosher violation)
        {"Item_ID": "I10", "Name": "Almond Milk", "Ingredients": "Almonds, Water", "Category": "Dairy-Alternative"},
        {"Item_ID": "I11", "Name": "Kosher Chicken Soup", "Ingredients": "Chicken breast, Carrots, Celery", "Category": "Meat"},
        {"Item_ID": "I12", "Name": "Healthy Trail Mix", "Ingredients": "Almonds, Cashews, Dried Cranberries", "Category": "Veg"}
    ]
    with open("workspace/incremental_data/new_shipment.json", "w") as f:
        json.dump(new_shipment, f, indent=2)

    # New Volunteers
    with open("workspace/incremental_data/new_volunteers.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Strength_Score", "Availability_Hours"])
        writer.writerows([
            ["V06", "Chris", "9", "5"],
            ["V07", "Sam", "5", "4"]
        ])
        
    with open("workspace/incremental_data/new_health_declarations.txt", "w") as f:
        f.write("V06 - Woke up with a temperature of 99.7F today. I feel strong though!\n") # TRAP: > 99.5F, must be banned.
        f.write("V07 - Clean bill of health, meditating daily.\n")

def build_turn_3():
    os.makedirs("workspace/sponsor", exist_ok=True)
    
    grant_text = """GRANT TERMS - TEXAS MUTUAL AID FUND
We are proud to support your grassroots wellness initiative. 

Funding Formula:
- Base Rate: $15.00 per approved volunteer hour.
- Multiplier: If the volunteer was assigned to 'Zone A' (Heavy/Bulk handling), they get a 1.5x multiplier ($22.50/hr).
- Penalty Clause: We do NOT fund any hours for volunteers who were rejected for health protocol violations.
- Exclusion: Any hours spent sorting rejected/non-compliant inventory do not count. For simplicity, we assume 100% of an approved volunteer's available hours are funded IF they are assigned to a valid zone and cleared health checks.

Please provide the final calculated grant request based on your processed rosters from all phases of the current operation.
"""
    with open("workspace/sponsor/grant_terms.txt", "w") as f:
        f.write(grant_text)

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
