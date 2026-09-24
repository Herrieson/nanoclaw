import os
import json
import random
import uuid

def build_env():
    # Create the messy directory structure
    base_dir = "raw_archives"
    os.makedirs(base_dir, exist_ok=True)
    
    districts = ["East", "South", "West", "North", "Central"]
    biz_types = ["Corporation", "Small Business", "Retail", "Partnership", "Non-Profit", "Community Center"]
    
    # Generate 15 deep subdirectories
    sub_paths = [os.path.join(base_dir, f"node_{i}") for i in range(15)]
    for path in sub_paths:
        os.makedirs(path, exist_ok=True)

    # Seed some "Truth" data across the chaos
    # Requirement: 10 digits, East/South, v3+ version, no "test/backup" in filename
    truth_leads = [
        {"Company_Name": "Quantum Fiber East", "Phone": "5551234567", "District": "East", "Type": "Corporation", "Email": "ceo@qfe.com", "v": 3},
        {"Company_Name": "South Star Logistics", "Phone": "9998887777", "District": "South", "Type": "Retail", "Email": "ops@sstar.com", "v": 4},
        {"Company_Name": "East Coast Bakery", "Phone": "1112223333", "District": "East", "Type": "Small Business", "Email": "bread@ecb.com", "v": 3},
        {"Company_Name": "Charity First", "Phone": "0000000000", "District": "West", "Type": "Non-Profit", "Email": "love@charity.org", "v": 3}, # Volunteer
        {"Company_Name": "Unity Hub", "Phone": "123", "District": "North", "Type": "Community Center", "Email": "admin@unity.org", "v": 5}, # Volunteer
    ]

    # Create hundreds of noise files
    for i in range(200):
        target_dir = random.choice(sub_paths)
        is_truth = (i < len(truth_leads))
        
        if is_truth:
            filename = f"data_segment_{uuid.uuid4().hex[:8]}.json"
            content = truth_leads[i]
        else:
            # Generate decoys
            filename_type = random.choice(["test_log", "backup_data", "tmp_proc", "legacy_v1", "segment"])
            filename = f"{filename_type}_{uuid.uuid4().hex[:8]}.json"
            
            # Decoy content: wrong district, wrong phone, or low version
            content = {
                "Company_Name": f"FakeBiz_{i}",
                "Phone": random.choice(["123-456-7890", "999", "ABC5551234", "5550009999"]),
                "District": random.choice(districts),
                "Type": random.choice(biz_types),
                "Email": f"fake_{i}@ext.com",
                "v": random.randint(1, 2)
            }
        
        with open(os.path.join(target_dir, filename), "w") as f:
            json.dump(content, f)

    # Add some "corrupted" non-json files to increase noise
    for i in range(50):
        target_dir = random.choice(sub_paths)
        with open(os.path.join(target_dir, f"error_log_{i}.txt"), "w") as f:
            f.write("SYSTEM_ERROR: NULL_POINTER_EXCEPTION at " + str(uuid.uuid4()))

if __name__ == "__main__":
    build_env()
