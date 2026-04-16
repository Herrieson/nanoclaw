import json
import os

def main():
    # Ensure the correct base directory exists
    base_dir = "assets/data_466"
    os.makedirs(base_dir, exist_ok=True)
    
    # Generate the mock dataset
    data = [
        {"id": 1, "location": "NJ", "category": "Education", "signatures": 120},
        {"id": 2, "location": "NY", "category": "Education", "signatures": 300},
        {"id": 3, "location": "NJ", "category": "Environment", "signatures": 85},
        {"id": 4, "location": "PA", "category": "Healthcare", "signatures": 50},
        {"id": 5, "location": "NJ", "category": "Education", "signatures": 45},
        {"id": 6, "location": "NJ", "category": "Environment", "signatures": 200},
        {"id": 7, "location": "NY", "category": "Healthcare", "signatures": 110},
        {"id": 8, "location": "PA", "category": "Environment", "signatures": 10},
    ]
    
    with open(os.path.join(base_dir, "raw_data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    # Generate the deliberately broken Python script
    bad_script = '''import json

def process():
    with open("raw_data.json", "r") as f:
        # BUG 1: Using json.loads on a file object instead of json.load
        data = json.loads(f)
    
    counts = {}
    for item in data:
        # BUG 2: Assignment operator instead of equality operator
        if item["location"] = "NJ":
            cat = item["category"]
            # BUG 3: Will raise KeyError because the key hasn't been initialized
            counts[cat] = counts[cat] + item["signatures"]
            
    with open("summary.txt", "w") as out:
        for c, count in counts.items():
            out.write(f"{c}: {count}\\n")

if __name__ == "__main__":
    process()
'''
    with open(os.path.join(base_dir, "process_data.py"), "w", encoding="utf-8") as f:
        f.write(bad_script)

if __name__ == "__main__":
    main()
