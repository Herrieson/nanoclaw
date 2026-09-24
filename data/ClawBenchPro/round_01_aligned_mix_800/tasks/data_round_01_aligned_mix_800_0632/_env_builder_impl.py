import os
import json
import csv

def build_env():
    # Create the primary working directory for the agent
    os.makedirs("campaign_data", exist_ok=True)
    
    # 1. Generate the influencer roster with a blacklist boolean
    roster = [
        {"name": "Aria_Style", "niche": "Fashion & Science", "tier": "A", "blacklisted": False},
        {"name": "BioTech_Bob", "niche": "R&D", "tier": "S", "blacklisted": True},
        {"name": "Chemistry_Chloe", "niche": "Cosmetics", "tier": "B", "blacklisted": False},
        {"name": "Derma_Diana", "niche": "Skincare", "tier": "A", "blacklisted": False},
        {"name": "Elegant_Eve", "niche": "Lifestyle", "tier": "C", "blacklisted": False},
        {"name": "Fake_User", "niche": "Spam", "tier": "F", "blacklisted": False}
    ]
    with open(os.path.join("campaign_data", "roster.json"), "w", encoding="utf-8") as f:
        json.dump(roster, f, indent=4)

    # 2. Generate raw engagement logs containing dirty data
    csv_path = os.path.join("campaign_data", "raw_engagement.csv")
    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Influencer_Name", "Likes", "Comments", "Shares"])
        # Aria_Style score: 1000 + (50*5) + (10*10) = 1350
        writer.writerow(["Aria_Style", "1000", "50", "10"]) 
        # BioTech_Bob score: 50000 + (1000*5) + (500*10) = 60000 (Highest, but blacklisted!)
        writer.writerow(["BioTech_Bob", "50000", "1000", "500"]) 
        # Chemistry_Chloe score: 2000 + (10*5) + (5*10) = 2100
        writer.writerow(["Chemistry_Chloe", "2000", "10", "5"]) 
        # Derma_Diana score: 1500 + (100*5) + (50*10) = 2500
        writer.writerow(["Derma_Diana", "1500", "100", "50"]) 
        # Elegant_Eve score: 500 + (20*5) + (2*10) = 620
        writer.writerow(["Elegant_Eve", "500", "20", "2"]) 
        # Dirty data row: Needs to be gracefully skipped by the agent
        writer.writerow(["Fake_User", "ERR", "N/A", ""]) 

    # 3. Generate the junior team's memo outlining the scoring logic
    memo_path = os.path.join("campaign_data", "junior_team_memo.txt")
    with open(memo_path, "w", encoding="utf-8") as f:
        f.write("MEMO: Q3 Derma-Tech Campaign Pre-Screening\n")
        f.write("Hi boss! We dumped the latest analytics in this folder.\n")
        f.write("As a reminder from our last marketing sync, our proprietary 'True Impact Score' is calculated as follows:\n")
        f.write("True Impact Score = Total Likes + (Total Comments * 5) + (Total Shares * 10)\n\n")
        f.write("We haven't had time to cross-reference this with legal's roster.json yet. Sorry!\n")

if __name__ == "__main__":
    build_env()
