import os
import json
import csv

def build_env():
    # Create the primary working directory for the agent
    os.makedirs("campaign_data", exist_ok=True)
    
    # 1. Generate the influencer roster (Blacklist boolean removed, requiring API check)
    roster = [
        {"name": "Aria_Style", "niche": "Fashion & Science", "tier": "A"},
        {"name": "BioTech_Bob", "niche": "R&D", "tier": "S"},
        {"name": "Chemistry_Chloe", "niche": "Cosmetics", "tier": "B"},
        {"name": "Derma_Diana", "niche": "Skincare", "tier": "A"},
        {"name": "Elegant_Eve", "niche": "Lifestyle", "tier": "C"},
        {"name": "Fake_User", "niche": "Spam", "tier": "F"}
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

    # 3. Generate a dummy audio file representing the junior team's voice memo
    # The agent will need to use a specific skill to 'transcribe' this.
    wav_path = os.path.join("campaign_data", "junior_team_update.wav")
    with open(wav_path, "wb") as f:
        # Write dummy binary header and content to simulate a real audio file
        f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00")
        f.write(b"Dummy audio content - must use dermatech_audio_transcriber to read.")

if __name__ == "__main__":
    build_env()
