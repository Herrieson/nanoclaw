import os
import csv

def build_env():
    # Create directories
    os.makedirs("sales_dumps", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Create region map
    region_data = [
        ["RepName", "Region"],
        ["Jim", "West"],
        ["Pam", "East"],
        ["Dwight", "North"],
        ["Angela", "South"],
        ["Oscar", "Central"]
    ]
    with open("region_map.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(region_data)

    # 2. Create noisy sales logs with License Codes instead of amounts
    # Rules for Agent to follow (from prompt): 
    # - Deduplicate by TX_ID
    # - Convert License_Code to Amount using provided Skills
    # - Ignore Amount < 1000
    # - Map RepName to Region
    
    # Value mapping (enforced by the Skill):
    # BIM-PRO: 4500
    # BIM-TRIAL: 900 (<1000 drop)
    # BIM-ENT: 15000
    # BIM-STD: 2500
    # BIM-UPG: 1200
    # BIM-EDU: 800 (<1000 drop)
    # BIM-RENEW: 3000
    # BIM-SITE: 5000

    log1 = [
        "TX101,Jim,BIM-PRO",
        "TX102,Pam,BIM-TRIAL",
        "TX103,Dwight,BIM-ENT"
    ]
    
    log2 = [
        "TX101,Jim,BIM-PRO",      # Duplicate
        "TX104,Angela,BIM-STD",
        "TX105,Pam,BIM-UPG",
        "TX103,Dwight,BIM-ENT"    # Duplicate
    ]
    
    log3 = [
        "TX106,Jim,BIM-EDU",
        "TX107,Dwight,BIM-RENEW",
        "TX104,Angela,BIM-STD",   # Duplicate
        "TX108,Oscar,BIM-SITE"
    ]
    
    with open("sales_dumps/log_week1.txt", "w") as f:
        f.write("\n".join(log1) + "\n")
        
    with open("sales_dumps/log_week2.txt", "w") as f:
        f.write("\n".join(log2) + "\n")
        
    with open("sales_dumps/log_week3.txt", "w") as f:
        f.write("\n".join(log3) + "\n")

if __name__ == "__main__":
    build_env()
