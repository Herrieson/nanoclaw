import os
import json
import csv
import random

def build_env():
    # Set seed for reproducible environment generation
    random.seed(42)

    # 1. Fragmented RSVPs
    os.makedirs("network_dumps/rsvps", exist_ok=True)
    
    valid_ids = []
    # Generate 500 RSVPs, with only a specific subset being valid
    for i in range(500):
        # Determine if this file will be valid
        # We manually inject exactly 20 valid files to control the exact portions
        is_valid = (i < 20)
        
        family_id = f"FAM_{1000 + i}"
        
        if is_valid:
            year = 2084
            status = "CONFIRMED"
            adults = random.randint(1, 4)
            cubs = random.randint(0, 3)
            valid_ids.append((family_id, adults, cubs))
        else:
            year = random.choice([2083, 2082, 2085, 2084])
            status = random.choice(["CANCELLED", "PENDING", "CORRUPTED", "CONFIRMED"])
            if year == 2084 and status == "CONFIRMED":
                status = "CANCELLED" # Ensure only our specific subset is valid
            adults = random.randint(1, 5)
            cubs = random.randint(0, 5)

        data = {
            "Family_ID": family_id,
            "Year": year,
            "Status": status,
            "Adults": adults,
            "Cubs_Under_5": cubs,
            "Metadata": "0xDEADBEEF"
        }
        
        # Further fragmentation: place in subdirectories
        sub_dir = f"network_dumps/rsvps/sector_{i % 5}"
        os.makedirs(sub_dir, exist_ok=True)
        
        with open(os.path.join(sub_dir, f"req_{i:04d}.json"), "w") as f:
            json.dump(data, f, indent=2)

    # Fixed valid stats: Total Adults = 50, Total Cubs = 20, Total Portions = 60.0
    # Let's override the generated valid_ids to guarantee exactly 50 adults and 20 cubs.
    adults_pool = 50
    cubs_pool = 20
    for idx, (fid, a, c) in enumerate(valid_ids):
        if idx == len(valid_ids) - 1:
            a_val, c_val = adults_pool, cubs_pool
        else:
            a_val = min(adults_pool, random.randint(1, 4))
            c_val = min(cubs_pool, random.randint(0, 2))
        
        # Overwrite the file with exact distribution
        sub_dir = f"network_dumps/rsvps/sector_{idx % 5}"
        with open(os.path.join(sub_dir, f"req_{idx:04d}.json"), "r") as f:
            d = json.load(f)
        d["Adults"] = a_val
        d["Cubs_Under_5"] = c_val
        with open(os.path.join(sub_dir, f"req_{idx:04d}.json"), "w") as f:
            json.dump(d, f, indent=2)
        
        adults_pool -= a_val
        cubs_pool -= c_val

    # 2. Med-Bay Records (Allergies)
    os.makedirs("med_bay", exist_ok=True)
    med_records = [["Patient_ID", "Family_ID", "Blood_Type", "Allergy_Warning"]]
    
    # Generate 1000 fake records
    for i in range(1000):
        med_records.append([
            f"PT_{random.randint(10000, 99999)}",
            f"FAM_{random.randint(1000, 2000)}",
            random.choice(["A", "B", "O", "AB", "Mutated"]),
            random.choice(["None", "Dust", "Rad-Roach", "None", "None"])
        ])
    
    # Inject Mutated-Peanut allergy to one of the VALID families to trigger the rule
    trigger_family = valid_ids[7][0] 
    med_records.append([
        "PT_99999", trigger_family, "O", "Mutated-Peanut"
    ])

    # Shuffle records
    headers = med_records[0]
    data_rows = med_records[1:]
    random.shuffle(data_rows)
    
    with open("med_bay/records.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data_rows)

    # 3. Archives Recipes
    os.makedirs("archives/recipes/food", exist_ok=True)
    os.makedirs("archives/recipes/drinks", exist_ok=True)
    
    recipes_data_1 = {
        "Scrap_Jollof": {
            "mutant_tomatoes": 0.5,
            "ash_onions": 0.25,
            "synth_rice": 0.5,
            "synth_peanut_oil": 0.1,  # Must be swapped
            "gecko_meat": 0.4
        },
        "Rad_Soup": {
            "dirty_water": 1.0,
            "gecko_meat": 0.2
        }
    }
    with open("archives/recipes/food/vol_1.json", "w") as f:
        json.dump(recipes_data_1, f, indent=4)
        
    recipes_data_2 = {
        "Spicy_Mutant_Plantains": {
            "glowing_plantains": 0.5,
            "red_dust_spices": 0.05
        }
    }
    with open("archives/recipes/food/vol_2.json", "w") as f:
        json.dump(recipes_data_2, f, indent=4)

    # Ingredients needed for 60 portions:
    # mutant_tomatoes: 30.0, ash_onions: 15.0, synth_rice: 30.0, rad_free_canola_oil: 6.0, gecko_meat: 24.0
    # glowing_plantains: 30.0, red_dust_spices: 3.0

    # 4. Comms Caravans
    os.makedirs("comms/caravans", exist_ok=True)
    
    # Caravan A: Crimson_Caravan (CSV format) - Total: 1425.0
    with open("comms/caravans/Crimson_Caravan.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["item_name", "price_per_unit", "stock_status"])
        writer.writerows([
            ["mutant_tomatoes", "10.0", "In Stock"],
            ["ash_onions", "5.0", "In Stock"],
            ["synth_rice", "8.0", "In Stock"],
            ["synth_peanut_oil", "50.0", "In Stock"],
            ["rad_free_canola_oil", "20.0", "In Stock"],
            ["gecko_meat", "15.0", "In Stock"],
            ["glowing_plantains", "6.0", "In Stock"],
            ["red_dust_spices", "50.0", "In Stock"],
            ["scrap_metal", "2.0", "In Stock"]
        ])

    # Caravan B: Wandering_Trader (JSON format) - Lowest Price! Total: 1416.0
    wandering_data = {
        "vendor": "Wandering_Trader",
        "inventory": [
            {"item": "mutant_tomatoes", "caps": 12.0},
            {"item": "ash_onions", "caps": 4.0},
            {"item": "synth_rice", "caps": 9.0},
            {"item": "synth_peanut_oil", "caps": 40.0},
            {"item": "rad_free_canola_oil", "caps": 18.0},
            {"item": "gecko_meat", "caps": 12.0},
            {"item": "glowing_plantains", "caps": 5.0},
            {"item": "red_dust_spices", "caps": 60.0},
            {"item": "fusion_core", "caps": 500.0}
        ]
    }
    with open("comms/caravans/Wandering_Trader.json", "w") as f:
        json.dump(wandering_data, f, indent=2)

    # Caravan C: Scavenger_Guild (TXT custom format) - Total: 1494.0
    with open("comms/caravans/Scavenger_Guild.txt", "w") as f:
        f.write("=== GUILD PRICING ===\n")
        f.write("mutant_tomatoes : 9.0\n")
        f.write("ash_onions : 8.0\n")
        f.write("synth_rice : 7.0\n")
        f.write("synth_peanut_oil : 45.0\n")
        f.write("rad_free_canola_oil : 25.0\n")
        f.write("gecko_meat : 16.0\n")
        f.write("glowing_plantains : 8.0\n")
        f.write("red_dust_spices : 40.0\n")
        f.write("radaway : 100.0\n")

if __name__ == "__main__":
    build_env()
