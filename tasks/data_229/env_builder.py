import os
import json

def create_environment():
    base_dir = "assets/data_229/messy_drive"
    os.makedirs(base_dir, exist_ok=True)
    
    # Subdirectories reflecting low conscientiousness
    dirs = [
        "archive_2022/jan",
        "new_stuff/drafts",
        "do_not_open",
        "designs_final_v2"
    ]
    for d in dirs:
        os.makedirs(os.path.join(base_dir, d), exist_ok=True)

    # Rates file
    rates_content = "material,rate_per_kg\nRecycled Steel,1.25\nFairTrade Aluminum,3.40\nScrap Copper,6.70\n"
    with open(os.path.join(base_dir, "archive_2022", "rates.csv"), "w") as f:
        f.write(rates_content)

    # Blueprint Data
    # 1. Valid & Matching (Wave, >500) -> Cost: 10 * 1.25 = 12.5
    bp1 = {"part_id": "BP-001", "motif": "Wave", "stamping_pressure": 600, "weight": 10.0, "material": "Recycled Steel"}
    # 2. Valid & Matching (leaf, >500) -> Cost: 5 * 6.70 = 33.5
    bp2 = {"part_id": "BP-002", "motif": "leaf", "stamping_pressure": 501, "weight": 5.0, "material": "Scrap Copper"}
    # 3. Valid & Matching (WAVE, >500) -> Cost: 20 * 3.40 = 68.0
    bp3 = {"part_id": "BP-003", "motif": "WAVE", "stamping_pressure": 800, "weight": 20.0, "material": "FairTrade Aluminum"}
    # 4. Valid & Matching (Leaf, >500) -> Cost: 8 * 1.25 = 10.0
    bp4 = {"part_id": "BP-004", "motif": "Leaf", "stamping_pressure": 700, "weight": 8.0, "material": "Recycled Steel"}
    
    # 5. Invalid (Wrong motif)
    bp5 = {"part_id": "BP-005", "motif": "Gear", "stamping_pressure": 600, "weight": 10.0, "material": "Recycled Steel"}
    # 6. Invalid (Pressure too low)
    bp6 = {"part_id": "BP-006", "motif": "Wave", "stamping_pressure": 500, "weight": 10.0, "material": "Recycled Steel"}
    # 7. Invalid (Missing weight) - should be skipped or handled gracefully
    bp7 = {"part_id": "BP-007", "motif": "Leaf", "stamping_pressure": 600, "material": "FairTrade Aluminum"}

    files_map = {
        "new_stuff/drafts/part1.json": json.dumps(bp1),
        "do_not_open/old_bp.json": json.dumps(bp2),
        "designs_final_v2/master.json": json.dumps(bp3),
        "archive_2022/jan/sketch.json": json.dumps(bp4),
        "new_stuff/gear.json": json.dumps(bp5),
        "designs_final_v2/low_pressure.json": json.dumps(bp6),
        "new_stuff/drafts/broken.json": json.dumps(bp7),
        # Malformed JSON file simulating corrupted data
        "do_not_open/corrupted.json": '{"part_id": "BP-008", "motif": "Wave", "stamping_pressure": 900, "weight": 10.0, "material": "Recycled Steel"' 
    }

    for path, content in files_map.items():
        with open(os.path.join(base_dir, path), "w") as f:
            f.write(content)

if __name__ == "__main__":
    create_environment()
