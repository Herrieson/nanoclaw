import os
import json
import csv
import random
import uuid
import time

def build_env():
    random.seed(42) # For reproducibility of the noise
    
    directories = [
        "communications/emails",
        "compliance_department/banned_lists",
        "campaign_data/daily_logs",
        "deliverables"
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)
        
    # 1. Generate Email Thread (The Rule Decoy & Truth)
    email_content = """From: Junior_Dev@company.com
To: Marketing_Manager@company.com
Date: Oct 12, 2023
Subject: RE: Q3 Derma-Tech Campaign Pre-Screening Metric

Hey Boss,
Just to confirm, we are NOT using the Q2 metric anymore (which was just Likes + Comments * 2). 
Per the meeting yesterday, the new proprietary 'True Impact Score' is officially locked in as:
True Impact Score = Total Likes + (Total Comments * 5) + (Total Shares * 10)

I was going to add 'Saves * 15' but the API didn't pull that data, so stick to the above.
I'll try to run the script later, but the IT migration broke my environment. Good luck!
"""
    with open("communications/emails/thread_oct_12_FINAL.txt", "w", encoding="utf-8") as f:
        f.write(email_content)
        
    with open("communications/emails/draft_q2_old.txt", "w", encoding="utf-8") as f:
        f.write("OLD MEMO: Q2 Score = Likes + Comments*2. DO NOT USE FOR Q3.")

    # 2. Generate Roster Database (Information Fragmentation)
    # 1000 regular influencers + 5 specially crafted ones for deterministic top ranks
    roster = []
    for _ in range(1000):
        roster.append({
            "id": uuid.uuid4().hex,
            "name": f"User_{random.randint(10000, 99999)}_{random.choice(['Skincare', 'Beauty', 'Tech', 'Lifestyle'])}"
        })
        
    # Inject deterministic targets
    target_1_banned = {"id": uuid.uuid4().hex, "name": "BioTech_Bob_Supreme"} # Highest score, but banned
    target_2_valid  = {"id": uuid.uuid4().hex, "name": "Aria_Style_Alpha"}    # Rank 1 valid
    target_3_banned = {"id": uuid.uuid4().hex, "name": "Scammy_Sam"}          # High score, banned
    target_4_valid  = {"id": uuid.uuid4().hex, "name": "Chemistry_Chloe_Beta"}# Rank 2 valid
    target_5_valid  = {"id": uuid.uuid4().hex, "name": "Derma_Diana_Gamma"}   # Rank 3 valid
    
    special_targets = [target_1_banned, target_2_valid, target_3_banned, target_4_valid, target_5_valid]
    roster.extend(special_targets)
    
    # Scatter roster into subdirectories based on first 2 chars of ID
    for person in roster:
        prefix = person["id"][:2]
        dir_path = os.path.join("roster_database", prefix)
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, f"{person['id']}.json"), "w") as f:
            json.dump(person, f)
            
    # 3. Generate Compliance Blacklists (Decoys & Multi-hop logic)
    base_time = int(time.time()) - 100000
    
    # Old banlist 1
    with open(f"compliance_department/banned_lists/banlist_{base_time}.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["banned_id", "reason"])
        for _ in range(20): writer.writerow([random.choice(roster)["id"], "spam"])
        writer.writerow([target_2_valid["id"], "old strike"]) # Was banned in the past, but not anymore!
        
    # Old banlist 2
    with open(f"compliance_department/banned_lists/banlist_{base_time + 5000}.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["banned_id", "reason"])
        for _ in range(20): writer.writerow([random.choice(roster)["id"], "spam"])
        
    # Latest banlist (The Truth)
    with open(f"compliance_department/banned_lists/banlist_{base_time + 10000}.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["banned_id", "reason"])
        for _ in range(30): writer.writerow([random.choice(roster)["id"], "spam"])
        writer.writerow([target_1_banned["id"], "fraud"])
        writer.writerow([target_3_banned["id"], "botting"])

    # 4. Generate Daily Logs (Scale & Noise)
    # We will generate 30 days of logs. We need to distribute the targets' stats across these files.
    # Target total scores to achieve:
    # T1_Banned: 150,000
    # T2_Valid:  120,000 (Winner 1)
    # T3_Banned: 100,000
    # T4_Valid:   80,000 (Winner 2)
    # T5_Valid:   60,000 (Winner 3)
    # Rest: < 40,000
    
    target_stats = {
        target_1_banned["id"]: {"likes": 50000, "comments": 10000, "shares": 5000}, # 50k + 50k + 50k = 150k
        target_2_valid["id"]:  {"likes": 40000, "comments": 8000, "shares": 4000},  # 40k + 40k + 40k = 120k
        target_3_banned["id"]: {"likes": 30000, "comments": 8000, "shares": 3000},  # 30k + 40k + 30k = 100k
        target_4_valid["id"]:  {"likes": 20000, "comments": 6000, "shares": 3000},  # 20k + 30k + 30k = 80k
        target_5_valid["id"]:  {"likes": 15000, "comments": 5000, "shares": 2000},  # 15k + 25k + 20k = 60k
    }
    
    for day in range(1, 31):
        file_path = os.path.join("campaign_data/daily_logs", f"log_day_{day:02d}.csv")
        with open(file_path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["influencer_id", "likes", "comments", "shares"])
            
            # Add some random standard users
            for _ in range(200):
                u = random.choice(roster)
                if u["id"] not in target_stats:
                    writer.writerow([u["id"], random.randint(0, 100), random.randint(0, 10), random.randint(0, 5)])
            
            # Inject daily chunk of targets
            for t_id, stats in target_stats.items():
                writer.writerow([
                    t_id, 
                    stats["likes"] // 30, 
                    stats["comments"] // 30, 
                    stats["shares"] // 30
                ])
                
            # Inject noise/corrupted rows to test robustness
            if day % 3 == 0:
                writer.writerow(["corrupted_uuid_abc", "ERR", "N/A", ""])
                writer.writerow([random.choice(roster)["id"], "NaN", "0", "0"])

if __name__ == "__main__":
    build_env()
