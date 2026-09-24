import os
import json
import random
import csv

def build_env():
    # 1. Create Directories
    os.makedirs("bids_dump", exist_ok=True)
    os.makedirs("communications", exist_ok=True)
    
    # 2. Generate Email Dump (Blacklist)
    emails = [
        "From: Boss | Subject: Mario Bros plumbing... | That guy charged me for lunch! DO NOT HIRE.",
        "From: Boss | Subject: Sparky's Electric | They nearly burned my shed down last summer. DO NOT HIRE.",
        "From: Boss | Subject: Woodpeckers Framing | Kept taking smoke breaks. DO NOT HIRE.",
        "From: Boss | Subject: Roofing pros | They are okay, maybe call them next week.",
        "From: Boss | Subject: Aqua King | Good work on the pipes last time.",
        "From: Boss | Subject: Cheap Plumbers | Flooded the basement. DO NOT HIRE."
    ]
    with open("communications/email_dump.txt", "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(emails))
        
    blacklisted_companies = ["Mario Bros", "Sparky's", "Woodpeckers", "Cheap Plumbers"]
    trades = ["plumbing", "electrical", "framing", "roofing", "concrete", "drywall"]
    bad_phrases = ["Union Dues", "City Permit Tax", "union dues", "CITY PERMIT TAX"]
    
    # Pre-determined Winners (Guaranteed to be the lowest valid bids)
    winners = {
        "plumbing": {"company": "Aqua King", "cost": 4500},
        "electrical": {"company": "Wire Wizards", "cost": 6200},
        "framing": {"company": "Steel Frame Co", "cost": 11000}
    }
    
    # We'll generate a lot of decoy data, some cheaper but invalid
    all_bids = []
    
    # Add winning bids
    all_bids.append({"trade": "plumbing", "company": "Aqua King", "base": 4000, "fees": 500, "notes": "Solid pipes.", "format": "csv"})
    all_bids.append({"trade": "electrical", "company": "Wire Wizards", "base": 6000, "fees": 200, "notes": "No extra tax.", "format": "json"})
    all_bids.append({"trade": "framing", "company": "Steel Frame Co", "base": 11000, "fees": 0, "notes": "Will work fast.", "format": "txt"})
    
    # Add Decoy Bids (Cheaper but invalid due to blacklist)
    all_bids.append({"trade": "plumbing", "company": "Mario Bros", "base": 3000, "fees": 100, "notes": "Quick fix.", "format": "csv"})
    all_bids.append({"trade": "electrical", "company": "Sparky's", "base": 4000, "fees": 0, "notes": "Cheap wires.", "format": "json"})
    all_bids.append({"trade": "framing", "company": "Woodpeckers", "base": 8000, "fees": 200, "notes": "Wood is good.", "format": "txt"})
    
    # Add Decoy Bids (Cheaper but invalid due to bad phrases)
    all_bids.append({"trade": "plumbing", "company": "State Pipes", "base": 3500, "fees": 500, "notes": "Includes union dues.", "format": "csv"})
    all_bids.append({"trade": "electrical", "company": "City Lights", "base": 5000, "fees": 500, "notes": "Includes City Permit Tax for zone A.", "format": "json"})
    all_bids.append({"trade": "framing", "company": "Union Frames", "base": 9000, "fees": 0, "notes": "We collect UNION DUES locally.", "format": "txt"})
    
    # Generate hundreds of random valid but expensive bids
    for i in range(250):
        t = random.choice(trades)
        fmt = random.choice(["csv", "json", "txt"])
        comp = f"Vendor_{i}"
        
        # Ensure expensive enough so they don't beat the winners
        base = random.randint(15000, 50000)
        fees = random.randint(0, 5000)
        
        notes_pool = ["Standard quote.", "Travel fee applied.", "Materials included."]
        # 10% chance to include a bad phrase
        if random.random() < 0.1:
            notes_pool.append(random.choice(bad_phrases))
            
        note = random.choice(notes_pool)
        
        all_bids.append({
            "trade": t,
            "company": comp,
            "base": base,
            "fees": fees,
            "notes": note,
            "format": fmt
        })
        
    random.shuffle(all_bids)
    
    # Write files into random nested directories
    months = [f"2023-{str(m).zfill(2)}" for m in range(1, 13)]
    regions = ["north", "south", "east", "west"]
    
    for i, bid in enumerate(all_bids):
        month = random.choice(months)
        region = random.choice(regions)
        dir_path = os.path.join("bids_dump", month, region)
        os.makedirs(dir_path, exist_ok=True)
        
        filepath = os.path.join(dir_path, f"quote_{i}.{bid['format']}")
        
        if bid['format'] == "csv":
            file_exists = os.path.isfile(filepath)
            with open(filepath, "w", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Company", "Trade", "BaseCost", "Fees", "Notes"])
                writer.writerow([bid["company"], bid["trade"], bid["base"], bid["fees"], bid["notes"]])
                
        elif bid['format'] == "json":
            data = {
                "contractor_info": {"name": bid["company"]},
                "job_details": {"type": bid["trade"]},
                "financials": {
                    "base_rate": bid["base"],
                    "surcharges": [{"amount": bid["fees"], "desc": "Assorted fees"}],
                },
                "additional_comments": bid["notes"]
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f)
                
        elif bid['format'] == "txt":
            content = f"--- QUOTE LOG ---\nTrade: {bid['trade']}\nCompany: {bid['company']}\n"
            content += f"Base Price: ${bid['base']}\nAdditional Fees: ${bid['fees']}\n"
            content += f"Notes: {bid['notes']}\n------------------\n"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

if __name__ == "__main__":
    build_env()
