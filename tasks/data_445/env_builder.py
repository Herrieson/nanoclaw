import os
import random

def build_env():
    base_dir = "assets/data_445"
    os.makedirs(f"{base_dir}/raw_claims", exist_ok=True)

    # Generate raw claims dump
    # Format: claim_id|patient_id|provider|diag_code|amount|date
    providers = ["Medicare", "Medicaid", "BlueCross", "Aetna", "Cigna"]
    diag_codes = ["A01.0", "E11.9", "I10", "J45.909", "J01.90", "J20.9", "M54.5", "Z00.00"]
    
    claims = []
    # Seed specific targets to ensure deterministic sum for verification
    claims.append("C1001|P105|Medicaid|J45.909|$450.75|2023-10-01")
    claims.append("C1005|P505|Medicaid|J20.9|$150.25|2023-10-03")
    claims.append("C1022|P911|Medicaid|J01.90|$80.50|2023-10-04")
    claims.append("C1033|P302|Medicaid|J45.909|$120.00|2023-10-05")
    claims.append("C1045|P888|Aetna|J45.909|$500.00|2023-10-03") # Wrong provider
    claims.append("C1050|P401|Medicaid|E11.9|$300.00|2023-10-02") # Wrong diag
    
    # Generate random noise
    random.seed(42)
    for i in range(1051, 1500):
        prov = random.choice(providers)
        diag = random.choice(diag_codes)
        amt = round(random.uniform(50.0, 1000.0), 2)
        claims.append(f"C{i}|P{random.randint(100,999)}|{prov}|{diag}|${amt:.2f}|2023-10-0{random.randint(1,9)}")
        
    # Shuffle claims
    random.shuffle(claims)
    
    with open(f"{base_dir}/raw_claims/claims_dump_2023.txt", "w") as f:
        f.write("\n".join(claims))

    # Broken script
    bad_script = """import csv

def send_report():
    total = 0
    # TODO: Someone update this to the real file, I lost the specs
    with open('temp.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += int(row['amount'])
    print(f"Total: {total}")

if __name__ == '__main__':
    send_report()
"""
    with open(f"{base_dir}/send_report.py", "w") as f:
        f.write(bad_script)

if __name__ == "__main__":
    build_env()
