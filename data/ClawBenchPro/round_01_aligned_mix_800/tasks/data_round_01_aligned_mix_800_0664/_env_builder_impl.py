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

    # 2. Create noisy sales logs
    # Rules for Agent to follow (from prompt): 
    # - Deduplicate by TX_ID
    # - Ignore Amount < 1000
    # - Map RepName to Region
    # Expected:
    # TX101: Jim, 4500 (West)
    # TX102: Pam, 900 -> DROP (<1000)
    # TX103: Dwight, 15000 (North)
    # TX104: Angela, 2500 (South)
    # TX105: Pam, 1200 (East)
    # TX106: Jim, 800 -> DROP (<1000)
    # TX107: Dwight, 3000 (North)
    # TX108: Oscar, 5000 (Central)
    
    log1 = [
        "TX101,Jim,4500",
        "TX102,Pam,900",
        "TX103,Dwight,15000"
    ]
    
    log2 = [
        "TX101,Jim,4500",      # Duplicate
        "TX104,Angela,2500",
        "TX105,Pam,1200",
        "TX103,Dwight,15000"   # Duplicate
    ]
    
    log3 = [
        "TX106,Jim,800",
        "TX107,Dwight,3000",
        "TX104,Angela,2500",   # Duplicate
        "TX108,Oscar,5000"
    ]
    
    with open("sales_dumps/log_week1.txt", "w") as f:
        f.write("\n".join(log1) + "\n")
        
    with open("sales_dumps/log_week2.txt", "w") as f:
        f.write("\n".join(log2) + "\n")
        
    with open("sales_dumps/log_week3.txt", "w") as f:
        f.write("\n".join(log3) + "\n")

if __name__ == "__main__":
    build_env()
