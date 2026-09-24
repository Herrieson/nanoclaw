import os
import json
import csv
import random

def build_env():
    random.seed(1176)
    
    # 1. Create directory structure
    dirs = [
        "donations/week_1", "donations/week_2", "donations/week_3", "donations/week_4",
        "inventory_master",
        "guidelines",
        "family_requests"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        
    # 2. Build Item Catalog
    items = {
        "ITM-101": "Canned Beans",
        "ITM-102": "Blankets",
        "ITM-103": "Canned Soup",
        "ITM-104": "Baby Formula",
        "ITM-105": "Diapers",
        "ITM-106": "Rice",
        "ITM-107": "Pasta",
        "ITM-108": "Cooking Oil",
        "ITM-109": "Oatmeal",
        "ITM-110": "Flour"
    }
    with open("inventory_master/item_catalog.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4)
        
    # 3. Build Status Codes (with a decoy version)
    v1_codes = [
        ["Code", "Description", "Usable"],
        ["C1", "Fresh", "True"],
        ["C2", "Expired", "False"]
    ]
    with open("guidelines/status_codes_v1_obsolete.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(v1_codes)
        
    v2_codes = [
        ["Code", "Description", "Usable"],
        ["A10", "Fresh/New", "True"],
        ["A11", "Good Condition", "True"],
        ["A12", "Blessed by Pastor", "True"],
        ["X90", "Expired", "False"],
        ["X91", "Spoiled/Moldy", "False"],
        ["X92", "Damaged Packaging", "False"],
        ["X93", "Contaminated", "False"]
    ]
    with open("guidelines/status_codes_v2.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(v2_codes)

    valid_codes = ["A10", "A11", "A12"]
    invalid_codes = ["X90", "X91", "X92", "X93"]
    all_codes = valid_codes + invalid_codes

    # 4. Generate scale donations (Mix of JSON, CSV, and Noise)
    for week in range(1, 5):
        folder = f"donations/week_{week}"
        for i in range(1, 41): # 40 files per week
            is_noise = random.choice([True, False, False, False]) # 25% chance of being noise
            ext = random.choice([".json", ".csv"])
            file_suffix = "_draft" if is_noise and random.choice([True, False]) else ""
            file_ext = ".bak" if is_noise and not file_suffix else ext
            
            filename = f"intake_log_{i:03d}{file_suffix}{file_ext}"
            filepath = os.path.join(folder, filename)
            
            # Generate 1-5 records per file
            records = []
            for _ in range(random.randint(1, 5)):
                records.append({
                    "item_id": random.choice(list(items.keys())),
                    "qty": random.randint(5, 50),
                    "status_code": random.choice(all_codes)
                })
                
            if ext == ".json" and not file_ext == ".bak":
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(records, f, indent=2)
            else:
                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["item_id", "qty", "status_code"])
                    for r in records:
                        writer.writerow([r["item_id"], r["qty"], r["status_code"]])
                        
    # 5. Generate Family Requests
    # 50 Families, some will get nothing, some will partially get things
    families = [f"F-{str(i).zfill(3)}" for i in range(1, 51)]
    item_names = list(items.values())
    
    for fam in families:
        num_requests = random.randint(1, 4)
        req_items = random.sample(item_names, num_requests)
        
        filepath = os.path.join("family_requests", f"msg_{fam}_inbox.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Blessings. This is a request form submitted online.\n")
            f.write(f"Family ID: {fam}\n")
            f.write(f"Needs:\n")
            for item in req_items:
                # Ask for quantities that will likely exhaust the inventory for some items
                f.write(f"- {item}: {random.randint(20, 100)}\n")
            f.write("Thank you for your generosity.\n")

if __name__ == "__main__":
    build_env()
