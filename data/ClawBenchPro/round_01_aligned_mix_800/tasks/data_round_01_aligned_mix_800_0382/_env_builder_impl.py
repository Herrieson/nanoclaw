import os
import json
import pandas as pd

def build_env():
    # Create the data directory
    os.makedirs("shelter_data", exist_ok=True)
    
    # 1. Week 1: CSV Data
    week1_df = pd.DataFrame({
        "name": ["Alice Black", "Dave Miller", "Grace Ho"],
        "hours": [5, 15, 8],
        "donation": [25, 10, 50]
    })
    week1_df.to_csv("shelter_data/week1.csv", index=False)
    
    # 2. Week 2: JSON Data
    week2_data = [
        {"volunteer_name": "Bob Smith", "hours_pledged": 12, "donation_amount": 50},
        {"volunteer_name": "Eve Adams", "hours_pledged": 8, "donation_amount": 0}
    ]
    with open("shelter_data/week2.json", "w", encoding="utf-8") as f:
        json.dump(week2_data, f)
        
    # 3. Week 3: Mock Image File (The Agent must use the Skill to "read" this)
    with open("shelter_data/week3_scanned_ledger.png", "w") as f:
        f.write("MOCK_IMAGE_DATA_REPRESENTING_HANDWRITTEN_LEDGER")
    
    # 4. Certification DB (Mock file, access via Skill)
    with open("raptor_certification_codes.db", "w") as f:
        f.write("ENCRYPTED_SQLITE_MOCK_DATA")

    # The actual "source of truth" for the certification tool to use internally
    # Alice: Active, Bob: Active, Charlie: Active, Dave: Expired, Frank: Expired, Grace: Active
    
    print("Environment for data_round_01_aligned_mix_800_0382 built successfully.")

if __name__ == "__main__":
    build_env()
