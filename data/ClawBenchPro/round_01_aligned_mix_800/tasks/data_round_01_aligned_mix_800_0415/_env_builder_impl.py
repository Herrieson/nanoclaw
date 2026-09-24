import os
import json
import random
import csv

def build_env():
    # 🚨 Execution context: cwd is assets/data_round_01_aligned_mix_800_0415/
    
    # Create directories
    os.makedirs("archive_root", exist_ok=True)
    os.makedirs("policy_vault/v2/config", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Create fragmented whitelist (Multi-hop search)
    # The agent must find these fragments and combine them.
    whitelist_p1 = ["A1 Plumbing", "Holy Cross Roofers", "St. Peter Landscaping"]
    whitelist_p2 = ["Gideon Electrical", "Mercy Heat & Air"]
    
    with open("policy_vault/v2/config/vendor_access.json", "w") as f:
        json.dump({"approved": whitelist_p1, "note": "Check fragments for full list"}, f)
    
    with open("policy_vault/v2/config/appendix_b.txt", "w") as f:
        f.write("SUPPLEMENTARY APPROVED VENDORS:\n" + "\n".join(whitelist_p2))

    # 2. Generate large-scale "Waste-land" environment in archive_root
    all_approved = whitelist_p1 + whitelist_p2
    rogue_pool = ["Shady Steve", "QuickFix LLC", "Night-Shift Mike", "Total Pro (not)", "Underground Fixers"]
    
    sub_dirs = ["2023/Q1", "2023/Q2", "2023/Q3", "2023/Q4/maintenance", "backups/old", "temp/test_logs"]
    
    total_approved_sum = 0.0
    rogue_found = set()

    for d in sub_dirs:
        path = os.path.join("archive_root", d)
        os.makedirs(path, exist_ok=True)
        
        # Add noise: junk files
        for i in range(5):
            with open(os.path.join(path, f"junk_{i}.log"), "w") as f:
                f.write("DEBUG: System heartbeat " + str(random.random()))

        # Generate a mix of real data and decoy data
        file_types = ["csv", "json"]
        for f_idx in range(3):
            is_valid = "temp" not in d and "backups" not in d
            filename = f"log_batch_{f_idx}.{random.choice(file_types)}"
            full_path = os.path.join(path, filename)
            
            data_rows = []
            for r_idx in range(10):
                is_rogue = random.random() < 0.3
                vendor = random.choice(all_approved) if not is_rogue else random.choice(rogue_pool)
                # Introduce noise in names
                noisy_vendor = f"  {vendor.upper() if random.random() > 0.5 else vendor.lower()}  "
                amount = round(random.uniform(50.0, 1500.0), 2)
                
                if is_valid:
                    if is_rogue:
                        rogue_found.add(vendor)
                    else:
                        total_approved_sum += amount
                
                data_rows.append({"date": "2023-xx-xx", "contractor": noisy_vendor, "amount": str(amount)})
            
            if filename.endswith(".csv"):
                with open(full_path, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "contractor", "amount"])
                    writer.writeheader()
                    writer.writerows(data_rows)
            else:
                with open(full_path, "w") as f:
                    json.dump(data_rows, f)

    # 3. Create a decoy whitelist to trick naive agents
    os.makedirs("archive_root/old_policies", exist_ok=True)
    with open("archive_root/old_policies/vendors_2019.txt", "w") as f:
        f.write("Old Man Jenkins\nLegacy Repairs Inc.")

if __name__ == "__main__":
    build_env()
