import os
import json
import csv

def build_env():
    base_dir = "assets/data_412"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Generate Tree Guide (JSON)
    tree_guide = {
        "Red Maple": "Loam",
        "White Pine": "Sandy",
        "River Birch": "Clay",
        "Douglas Fir": "Acidic"
    }
    with open(os.path.join(base_dir, "tree_guide.json"), "w") as f:
        json.dump(tree_guide, f, indent=4)

    # 2. Generate Zones (CSV)
    zones = [
        {"Zone_ID": "Z-North", "Soil_Type": "Loam", "Max_Capacity": 3},
        {"Zone_ID": "Z-South", "Soil_Type": "Sandy", "Max_Capacity": 2},
        {"Zone_ID": "Z-East", "Soil_Type": "Clay", "Max_Capacity": 2},
        {"Zone_ID": "Z-West", "Soil_Type": "Loam", "Max_Capacity": 2},
        {"Zone_ID": "Z-Central", "Soil_Type": "Sandy", "Max_Capacity": 1}
    ]
    with open(os.path.join(base_dir, "zones.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Zone_ID", "Soil_Type", "Max_Capacity"])
        writer.writeheader()
        writer.writerows(zones)

    # 3. Generate Messy Logs
    # Logic: 
    # Loam capacity: 3 + 2 = 5. Maples: Alice, Frank, Grace, Hank, Ivy, Jack (Jack should be skipped)
    # Sandy capacity: 2 + 1 = 3. Pines: Bob, David, Eve, Liam (Liam skipped)
    # Clay capacity: 2. Birches: Charlie, Mia (All fit)
    
    logs = [
        "2023-04-10 08:12:01 [INFO] Server started successfully.",
        "2023-04-10 08:15:22 [WARN] High memory usage detected.",
        '2023-04-10 08:16:05 [PAYLOAD] {"name": "Alice", "grade": 10, "tree": "Red Maple"}',
        "2023-04-10 08:16:06 [DEBUG] Connection timeout from 192.168.1.5",
        '2023-04-10 08:17:10 [PAYLOAD] {"name": "Bob", "grade": 11, "tree": "White Pine"}',
        '2023-04-10 08:18:00 [PAYLOAD] {"name": "Charlie", "grade": 9, "tree": "River Birch"}',
        '2023-04-10 08:18:01 [PAYLOAD] {"name": "Alice", "grade": 10, "tree": "Red Maple"}', # Duplicate
        "2023-04-10 08:19:15 [ERROR] Database lock acquisition failed.",
        '2023-04-10 08:20:05 [PAYLOAD] {"name": "David", "grade": 12, "tree": "White Pine"}',
        '2023-04-10 08:21:30 [PAYLOAD] {"name": "Eve", "grade": 10, "tree": "White Pine"}',
        '2023-04-10 08:22:12 [PAYLOAD] {"name": "Frank", "grade": 9, "tree": "Red Maple"}',
        '2023-04-10 08:22:15 [PAYLOAD] {"name": "Grace", "grade": 11, "tree": "Red Maple"}',
        '2023-04-10 08:23:05 [PAYLOAD] {"name": "Hank", "grade": 10, "tree": "Red Maple"}',
        '2023-04-10 08:24:00 [PAYLOAD] {"name": "Ivy", "grade": 12, "tree": "Red Maple"}',
        '2023-04-10 08:24:05 [PAYLOAD] {"name": "Frank", "grade": 9, "tree": "Red Maple"}', # Duplicate
        '2023-04-10 08:25:10 [PAYLOAD] {"name": "Jack", "grade": 9, "tree": "Red Maple"}', # Exceeds capacity
        '2023-04-10 08:26:00 [PAYLOAD] {"name": "Liam", "grade": 11, "tree": "White Pine"}', # Exceeds capacity
        '2023-04-10 08:27:00 [PAYLOAD] {"name": "Mia", "grade": 10, "tree": "River Birch"}',
        "2023-04-10 08:30:00 [INFO] Shutting down."
    ]

    with open(os.path.join(base_dir, "volunteer_logs.txt"), "w") as f:
        for line in logs:
            f.write(line + "\n")

if __name__ == "__main__":
    build_env()
