import os
import json
import random

def build_env():
    # Execute in the local cwd as requested.
    # Create the fragmented "wasteland" structure
    os.makedirs("registry/backups", exist_ok=True)
    os.makedirs("archive/temp_cache", exist_ok=True)
    os.makedirs("community_fair_prep", exist_ok=True)

    # 1. The "Truth" - Authorized Personnel
    # Hidden in a nested directory with a misleading name
    authorized = ["Sarah_V", "David_K", "Miriam_A", "Jamal_X", "Chloe_Z", "Ezra_W"]
    with open("registry/backups/master_roster_final_v2.json", "w") as f:
        json.dump({"authorized_personnel": authorized, "version": "Current_Season", "note": "Only use this for the 2024 fair"}, f)

    # 2. Noise - Old Roster
    with open("registry/old_roster_2022.json", "w") as f:
        json.dump({"authorized_personnel": ["Chad", "Karen", "Steve"], "version": "Deprecated"}, f)

    # 3. Scale Simulation - Shard Generation (100 files)
    # Some are "Current_Season", some are "Old_Data", some are "Corrupted"
    names_pool = authorized + ["Chad", "Karen", "Bot_123", "Unknown_User"]
    healthy_items = [("Organic_Apples", 50), ("Meditation_Mat", 12), ("Social_Justice_Zine", 100), ("Quinoa_Pack", 30), ("Herbal_Tea", 40)]
    junk_items = [("Sugar_Soda_Red", 500), ("Processed_Cheese_Goop", 20), ("Fried_Lard_Chips", 100), ("Candy_Bar_Mega", 200)]

    for i in range(100):
        filename = f"archive/shard_{i:03d}.log"
        is_valid = random.choice([True, False, False]) # 1/3 chance of being relevant data
        
        content = []
        if is_valid:
            content.append("## STATUS: Current_Season")
            # Add some random volunteer data
            for _ in range(random.randint(1, 3)):
                p = random.choice(names_pool)
                h = round(random.uniform(1.0, 5.0), 1)
                content.append(f"VOLUNTEER_ENTRY: {p} | HOURS: {h}")
            # Add some donation data
            for _ in range(random.randint(1, 2)):
                item, qty = random.choice(healthy_items + junk_items)
                content.append(f"DONATION: {item} | QTY: {qty} | CAT: Wellness_Check")
        else:
            content.append("## STATUS: Legacy_Archive_2022")
            content.append("DATA_CORRUPTED_OR_OUTDATED")
            content.append(f"DUMP: {random.getrandbits(32)}")

        with open(filename, "w") as f:
            f.write("\n".join(content))

    # 4. Decoy - A fake manifest in the root to trick lazy agents
    with open("donations_SUMMARY_FINAL_DO_NOT_USE.csv", "w") as f:
        f.write("Item,Quantity\nFake_Apples,0\nSoda_Poison,9999")

if __name__ == "__main__":
    build_env()
