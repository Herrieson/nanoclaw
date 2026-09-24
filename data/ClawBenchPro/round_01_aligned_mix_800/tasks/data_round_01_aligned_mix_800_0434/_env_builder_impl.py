import os
import json
import csv
import random

def build_env():
    # Root directory for the mess
    base_dir = "archive_dump"
    os.makedirs(base_dir, exist_ok=True)

    titles = ["The Amazing Spider-Man", "X-Men", "Batman", "Fantastic Four", "The Avengers", 
              "Iron Man", "Green Lantern", "Action Comics", "Detective Comics", "Flash"]
    
    # Function to create a "Verified" shard (CSV or JSON)
    def create_verified_shard(path, data, file_type="csv"):
        if file_type == "csv":
            with open(path, "w", newline='') as f:
                f.write("# STATUS: VERIFIED\n") # The crucial hint
                writer = csv.DictWriter(f, fieldnames=["Title", "Issue", "Condition_Score", "Market_Value"])
                writer.writeheader()
                writer.writerows(data)
        else:
            with open(path, "w") as f:
                # JSON with meta-tag
                json_data = {"metadata": {"status": "VERIFIED"}, "items": data}
                json.dump(json_data, f)

    # Function to create "Decoy" junk
    def create_decoy(path):
        with open(path, "w") as f:
            f.write(f"DEPRECATED LOG\nTIMESTAMP: {random.randint(1000, 9999)}\nDATA: CORRUPTED")

    # 1. Create a deep, confusing directory tree
    for i in range(5):
        sub_dir = os.path.join(base_dir, f"sector_0{i}")
        os.makedirs(sub_dir, exist_ok=True)
        for j in range(3):
            deep_dir = os.path.join(sub_dir, f"node_{j}")
            os.makedirs(deep_dir, exist_ok=True)
            
            # Fill with decoys
            for k in range(20):
                create_decoy(os.path.join(deep_dir, f"junk_{k}.log"))
                create_decoy(os.path.join(deep_dir, f"backup_v{k}.tmp"))

    # 2. Scatter the "Verified" shards
    # Shard 1: High value Spider-Man (CSV)
    shard1_path = os.path.join(base_dir, "sector_01/node_2/inventory_shard_A.csv")
    create_verified_shard(shard1_path, [
        {"Title": "The Amazing Spider-Man", "Issue": "129", "Condition_Score": "9.2", "Market_Value": "2500"},
        {"Title": "X-Men", "Issue": "1", "Condition_Score": "4.5", "Market_Value": "12000"}, # Will be filtered (low score)
        {"Title": "Batman", "Issue": "181", "Condition_Score": "8.0", "Market_Value": "1500"}
    ])

    # Shard 2: Duplicate with better score + some missing values (JSON)
    shard2_path = os.path.join(base_dir, "sector_03/node_0/recovered_data.json")
    create_verified_shard(shard2_path, [
        {"Title": "The Amazing Spider-Man", "Issue": "129", "Condition_Score": "9.8", "Market_Value": "4500"}, # Better score than Shard A
        {"Title": "Iron Man", "Issue": "1", "Condition_Score": "9.6", "Market_Value": "5000"},
        {"Title": "Fantastic Four", "Issue": "48", "Condition_Score": "9.0", "Market_Value": ""}, # Missing value, filter out
    ], file_type="json")

    # 3. Generate Scale: 200 more "Verified" items across 10 random small shards
    all_titles = titles * 20
    for s in range(10):
        shard_data = []
        for _ in range(20):
            shard_data.append({
                "Title": random.choice(titles),
                "Issue": str(random.randint(1, 300)),
                "Condition_Score": str(round(random.uniform(1.0, 10.0), 1)),
                "Market_Value": str(random.randint(50, 2000))
            })
        path = os.path.join(base_dir, f"sector_0{s%5}/node_{s%3}/shard_bulk_{s}.csv")
        create_verified_shard(path, shard_data)

    # 4. Add "Shadow Backups" (Fake data - no VERIFIED tag)
    with open(os.path.join(base_dir, "sector_00/node_0/shadow_copy.csv"), "w") as f:
        f.write("Title,Issue,Condition_Score,Market_Value\n")
        f.write("Action Comics,1,10.0,1000000\n") # Fake high value to bait the Agent

if __name__ == "__main__":
    build_env()
