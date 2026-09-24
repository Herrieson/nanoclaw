import os
import json
import csv
import random

def build_env():
    # 1. Create Base Directories
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("stockroom_logs/2023-10-26", exist_ok=True)
    os.makedirs("stockroom_logs/2023-10-27", exist_ok=True)
    os.makedirs("pos_data/yesterday_10_26", exist_ok=True)
    os.makedirs("hr", exist_ok=True)

    # 2. Build HR Data (Multi-hop starting point & Rules)
    staff_data = [
        ["Emp_Name", "Emp_ID", "Role"],
        ["Sarah", "EMP-1001", "Server"],
        ["John", "EMP-1002", "Server"],
        ["Mike", "EMP-1003", "Server"],
        ["Danny", "EMP-8492", "Helper"],
        ["Chris", "EMP-8833", "Helper"]
    ]
    with open("hr/staff.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(staff_data)

    tip_policy = {
        "description": "Bartender Helper Tip Cut Rules",
        "default_cut": 0.20,
        "rules": [
            {
                "condition": "party_size >= 8",
                "cut": 0.15,
                "priority": 1,
                "note": "Large parties require more kitchen staff, helper cut drops."
            },
            {
                "condition": "server == 'Sarah'",
                "cut": 0.25,
                "priority": 2,
                "note": "Sarah handles VIPs, helpers get more."
            }
        ],
        "precedence": "Rule 1 (party_size) overrides Rule 2 (server) if both apply."
    }
    with open("hr/tip_policy.json", "w", encoding="utf-8") as f:
        json.dump(tip_policy, f, indent=2)

    # 3. Build Fragmented & Noisy Recipes
    random.seed(42)
    ingredients_pool = ["Gin", "Rum", "Vodka", "Tequila", "Lime Juice", "Lemon Juice", "Simple Syrup", "Soda Water", "Mint"]
    
    # Generate 50 noisy subdirectories with 10 random recipes each
    for i in range(1, 21):
        cat_dir = f"recipes/category_{i}"
        os.makedirs(cat_dir, exist_ok=True)
        for j in range(10):
            fake_recipe = {
                "name": f"Classic Drink {i}-{j}",
                "author": random.choice(["Admin", "System", "Old_Bartender"]),
                "status": "archived",
                "ingredients": random.sample(ingredients_pool, 3)
            }
            with open(f"{cat_dir}/recipe_{j}.json", "w", encoding="utf-8") as f:
                json.dump(fake_recipe, f, indent=2)

    # Inject Danny's real recipes secretly
    danny_recipes = [
        {
            "name": "Irish Sunrise",
            "author": "Danny",
            "status": "pitch_ready",
            "ingredients": ["Tequila", "Orange Juice", "Grenadine"]
        },
        {
            "name": "Missouri Mule",
            "author": "Danny",
            "status": "pitch_ready",
            "ingredients": ["Vodka", "Ginger Beer", "Lime Juice"]
        },
        {
            "name": "Midwest Fidget",
            "author": "Danny",
            "status": "pitch_ready",
            "ingredients": ["Bourbon", "Bitters", "Simple Syrup"]
        }
    ]
    # Scatter them in random existing directories
    target_dirs = ["recipes/category_3", "recipes/category_12", "recipes/category_18"]
    for idx, r in enumerate(danny_recipes):
        with open(f"{target_dirs[idx]}/danny_idea_{idx}.json", "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2)

    # 4. Build Messy Stockroom Logs
    # Yesterday's logs (Noise)
    with open("stockroom_logs/2023-10-26/inventory.txt", "w") as f:
        f.write("Everything is fully stocked.\n- Grenadine: 10 bottles\n- Bourbon: 5 bottles")

    # Today's early draft (Decoy - claims items are in stock)
    with open("stockroom_logs/2023-10-27/0800_draft_count.log", "w", encoding="utf-8") as f:
        f.write("MORNING DRAFT 08:00 AM\nBourbon: 2\nGrenadine: 1\nVodka: 10\nGinger Beer: 50\nLime Juice: 5\nBitters: 2\nSimple Syrup: 3")

    # Today's final count (The Truth)
    final_log_content = """
    === FINAL COUNT - 10/27 11:45 AM ===
    Count signed off by Manager. Do NOT use previous drafts.
    
    [AVAILABLE IN STOCK]
    - Vodka: 5 btls
    - Tequila: 2 btls
    - Ginger Beer: 24 cans
    - Lime Juice: 3 liters
    - Orange Juice: 2 liters
    - Bitters: 1 btl
    - Simple Syrup: 1 btl
    
    [86'd / EMPTY / DO NOT USE]
    - Grenadine (Completely out until next week!)
    - Bourbon (Supplier forgot it, out of stock)
    - Mint (Rotten, threw it away)
    """
    with open("stockroom_logs/2023-10-27/1145_final_count.txt", "w", encoding="utf-8") as f:
        f.write(final_log_content)

    # 5. Build Large-Scale, Fragmented POS Data
    servers = ["Sarah", "John", "Mike"]
    helpers = ["EMP-8492", "EMP-8833"] # Danny vs Chris
    statuses = ["COMPLETED", "COMPLETED", "COMPLETED", "VOID"]

    # 12 hours of data
    tx_id_counter = 1000
    for hour in range(12, 24):
        chunk_file = f"pos_data/yesterday_10_26/hourly_export_{hour}00.csv"
        with open(chunk_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["TXN_ID", "Server_Name", "Helper_ID", "Tip_Amount", "Party_Size", "Status"])
            
            # Generate ~50 rows per file
            for _ in range(50):
                tx_id = f"TXN-{tx_id_counter}"
                server = random.choice(servers)
                helper = random.choice(helpers)
                tip = round(random.uniform(5.0, 150.0), 2)
                party = random.choice([2, 4, 5, 8, 10, 12])
                status = random.choice(statuses)
                
                # Make sure we have some predictable records for Danny to test logic
                # Random generation is fine as long as the Agent parses all of them accurately.
                writer.writerow([tx_id, server, helper, f"{tip:.2f}", party, status])
                tx_id_counter += 1

if __name__ == "__main__":
    build_env()
