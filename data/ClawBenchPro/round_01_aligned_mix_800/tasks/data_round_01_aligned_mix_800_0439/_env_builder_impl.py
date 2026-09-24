import os
import json
import csv
import random

def build_env():
    # Set deterministic seed so evaluation is repeatable
    random.seed(4242)

    # 1. Create directory structure
    dirs = [
        "deliverables",
        "policies",
        "employees"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 2. Generate Employees & Write to regional CSVs
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", "George", "Hannah", "Ian", "Jane", "Kevin", "Laura", "Mike", "Nina", "Oscar", "Paula"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson"]
    
    employees = {}
    regions = {"East": [], "West": [], "Central": []}
    
    for i in range(1, 501):
        emp_id = f"EMP_{i:04d}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        employees[emp_id] = name
        region = random.choice(list(regions.keys()))
        regions[region].append({"emp_id": emp_id, "full_name": name})

    for region, emps in regions.items():
        with open(f"employees/roster_{region}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["emp_id", "full_name"])
            writer.writeheader()
            writer.writerows(emps)

    # 3. Generate Policies
    # Decoy policy (v1)
    with open("policies/policy_v1.json", "w") as f:
        json.dump({
            "version": 1,
            "valid_expense_codes": ["TRV", "TRN", "MEA", "BWG"], 
            "contraband_codes": ["GFT"]
        }, f, indent=4)
    
    # Decoy policy (v2)
    with open("policies/policy_v2.json", "w") as f:
        json.dump({
            "version": 2,
            "valid_expense_codes": ["CODE_1", "CODE_2"], 
            "contraband_codes": ["CODE_3"]
        }, f, indent=4)

    # True policy (v4)
    with open("policies/policy_v4.json", "w") as f:
        json.dump({
            "version": 4,
            "valid_expense_codes": ["V_TRV", "V_TRN", "V_MEA"], 
            "contraband_codes": ["X_BWG"]
        }, f, indent=4)

    # 4. Generate Claims Data
    valid_codes = ["V_TRV", "V_TRN", "V_MEA"]
    contraband_code = "X_BWG"
    other_codes = ["O_GFT", "O_ENT", "O_MISC"] # Valid in syntax, but rejected by policy

    all_claims = []
    expected_total = 0.0
    bird_watchers = set()

    # Generate 1500 unique claims
    for i in range(1, 1501):
        claim_id = f"CLM_{i:06d}"
        emp_id = random.choice(list(employees.keys()))
        
        # Determine code
        rand_val = random.random()
        if rand_val < 0.7:
            code = random.choice(valid_codes)
        elif rand_val < 0.85:
            code = contraband_code
        else:
            code = random.choice(other_codes)

        # Determine amount
        raw_amount = round(random.uniform(10.0, 1500.0), 2)
        
        # Format amount with noise
        fmt_choice = random.randint(1, 4)
        if fmt_choice == 1:
            amt_str = f"${raw_amount:,.2f}"
        elif fmt_choice == 2:
            amt_str = f"{raw_amount:.2f} USD"
        elif fmt_choice == 3:
            amt_str = f"{raw_amount:,.2f}"
        else:
            amt_str = str(raw_amount)

        claim = {
            "claim_id": claim_id,
            "emp_id": emp_id,
            "expense_code": code,
            "amount": amt_str
        }
        all_claims.append(claim)

        # Track truth
        if code in valid_codes:
            expected_total += raw_amount
        if code == contraband_code:
            bird_watchers.add(employees[emp_id])

    # Inject 300 duplicate claims (same claim_id and data)
    duplicates = random.sample(all_claims, 300)
    all_claims.extend(duplicates)
    
    # Shuffle all claims
    random.shuffle(all_claims)

    # 5. Scatter Claims into nested directories
    def chunk_list(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    chunks = list(chunk_list(all_claims, 50))
    
    # Create random deep directories
    months = ["08", "09", "10", "11"]
    days = [f"{d:02d}" for d in range(1, 29)]
    
    chunk_idx = 0
    for m in months:
        for d in days:
            if chunk_idx >= len(chunks):
                break
            dir_path = os.path.join("claims_dump", "2023", m, d)
            os.makedirs(dir_path, exist_ok=True)
            
            # Write valid batch file
            file_path = os.path.join(dir_path, f"batch_{chunk_idx:04d}.json")
            with open(file_path, "w") as f:
                json.dump(chunks[chunk_idx], f, indent=4)
            chunk_idx += 1
            
            # Write decoy / draft file (huge invalid amounts to ruin math if not filtered)
            decoy_path = os.path.join(dir_path, f"draft_batch_{chunk_idx:04d}.json")
            with open(decoy_path, "w") as f:
                json.dump([{
                    "claim_id": "CLM_999999",
                    "emp_id": "EMP_0001",
                    "expense_code": "V_TRV",
                    "amount": "$99,999,999.00"
                }], f)
                
            # Write .bak file decoy
            bak_path = os.path.join(dir_path, f"batch_{chunk_idx:04d}.bak")
            with open(bak_path, "w") as f:
                json.dump([{
                    "claim_id": "CLM_888888",
                    "emp_id": "EMP_0002",
                    "expense_code": "X_BWG",
                    "amount": "100.00"
                }], f)

    # Save expected truth for testing/validation purposes (hidden file)
    with open(".expected_solution.json", "w") as f:
        json.dump({
            "total_approved_amount": round(expected_total, 2),
            "bird_watcher_names": sorted(list(bird_watchers))
        }, f, indent=4)

if __name__ == "__main__":
    build_env()
