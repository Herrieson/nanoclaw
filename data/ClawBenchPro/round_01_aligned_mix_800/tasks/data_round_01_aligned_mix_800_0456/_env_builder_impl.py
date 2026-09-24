import os
import random
import json

def build_env():
    # 🚨 Execution context: cwd is already set to the asset directory.
    base_dir = "production_logs"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create a deep, confusing directory structure
    sub_paths = [
        "sector_7/diagnostics/archive",
        "sector_7/sensor_data/temp",
        "maintenance/cycle_reports/2023",
        "human_resources/personal_backups/dump",
        "storage/overflow/node_B"
    ]
    for path in sub_paths:
        os.makedirs(os.path.join(base_dir, path), exist_ok=True)

    # 2. Define the "Truth" - Vintage Items to find
    vintage_items = [
        ("1940s wool trench coat", 125.50),
        ("Vintage 1950s workwear chore coat", 55.00),
        ("1970s flared corduroy pants", 22.75),
        ("Antique silk cravat [V-S]", 45.00),
        ("1960s fedora hat", 40.00),
        ("Victorian era cufflinks [V-S]", 88.20),
        ("Vintage denim jacket", 65.00)
    ]

    # 3. Define Noise - Fishing, Groceries, Machine Logs
    noise_templates = [
        "Machine Sensor {id}: Vibration at {val}Hz. Status: CRITICAL",
        "Groceries: Milk, Bread, Eggs - ${cost}",
        "Fishing Gear: {item} - ${cost}",
        "System Log: Buffer overflow at 0x{hex_addr}",
        "Reminder: Shift starts at 6:00 AM. Don't be late again."
    ]
    fishing_items = ["Carbon Fiber Rod", "Spinning Reel", "Tackle Box", "Live Bait", "Waders"]

    # 4. Distribute files
    total_files = 120
    truth_indices = random.sample(range(total_files), len(vintage_items))
    
    for i in range(total_files):
        target_path = os.path.join(base_dir, random.choice(sub_paths))
        file_ext = random.choice([".log", ".fragment", ".txt", ".tmp"])
        filename = f"data_stream_{i:04d}{file_ext}"
        
        content = []
        # Add 10-20 lines of noise to every file
        for _ in range(random.randint(10, 20)):
            ntype = random.randint(0, 4)
            if ntype == 0:
                content.append(noise_templates[0].format(id=random.randint(100, 999), val=random.uniform(50, 500)))
            elif ntype == 1:
                content.append(noise_templates[1].format(cost=random.uniform(5, 100)))
            elif ntype == 2:
                content.append(noise_templates[2].format(item=random.choice(fishing_items), cost=random.uniform(20, 150)))
            elif ntype == 3:
                content.append(noise_templates[3].format(hex_addr=hex(random.randint(4096, 65535))))
            else:
                content.append(noise_templates[4])

        # Inject truth if this index is chosen
        if i in truth_indices:
            item, cost = vintage_items.pop()
            # Randomly place the truth line in the file
            content.insert(random.randint(0, len(content)), f"MEMO: Purchased {item}. Final cost: ${cost:.2f}. Need to hide this.")

        with open(os.path.join(target_path, filename), "w", encoding="utf-8") as f:
            f.write("\n".join(content))

if __name__ == "__main__":
    build_env()
