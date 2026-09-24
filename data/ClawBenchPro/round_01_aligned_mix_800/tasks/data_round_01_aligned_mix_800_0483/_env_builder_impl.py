import os
import json
import csv
import random
import uuid

def build_env():
    # Setup directories
    os.makedirs("agency_drop/submissions", exist_ok=True)
    os.makedirs("agency_drop/legal_archives", exist_ok=True)
    os.makedirs("agency_drop/finance", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    random.seed(1205) # Predictable randomness
    
    # 1. Defined Targets & Traps
    fixed_bands = [
        # --- TRUE SURVIVORS ---
        {
            "id": "B-SURV-1001", "name": "Neon Echoes", "genre": "Dark Synth-pop",
            "scandal_raw": "false", "legal": "CLEARED", "price_raw": "$3,500.00"
        },
        {
            "id": "B-SURV-1002", "name": "The Crimson Void", "genre": "Shoegaze / Dream Pop",
            "scandal_raw": "No", "legal": "WARNING", "price_raw": "4800 USD"
        },
        {
            "id": "B-SURV-1003", "name": "Electric Dreams", "genre": "Lo-Fi synth",
            "scandal_raw": "False", "legal": None, "price_raw": "2,450.50"
        },
        # --- TRAINED DECOYS (Must fail one condition) ---
        { # Fails budget
            "id": "B-FAIL-2001", "name": "Midnight Runners", "genre": "Synthwave",
            "scandal_raw": "false", "legal": "CLEARED", "price_raw": "$5,500.00" 
        },
        { # Fails basic scandal check
            "id": "B-FAIL-2002", "name": "Rebel Yell", "genre": "Synth-pop",
            "scandal_raw": "true", "legal": "CLEARED", "price_raw": "$2,000" 
        },
        { # Fails legal ban
            "id": "B-FAIL-2003", "name": "The Blacklisted", "genre": "Industrial Synth",
            "scandal_raw": "false", "legal": "PERMANENT_BAN", "price_raw": "$1,500" 
        },
        { # Fails genre
            "id": "B-FAIL-2004", "name": "Fading Light", "genre": "Post-punk Revival",
            "scandal_raw": "false", "legal": "CLEARED", "price_raw": "3000" 
        }
    ]

    all_bands = []
    
    # Generate 400 random noise bands that will definitely fail at least one check
    regions = ['NA', 'EU', 'APAC', 'LATAM']
    months = ['01', '02', '03', '04', '05', '06']
    genres_noise = ['Pop', 'Rock', 'Metal', 'Jazz', 'Classical', 'Hip Hop', 'Country']
    
    for _ in range(400):
        b_id = f"B-NOISE-{str(uuid.uuid4())[:8].upper()}"
        # Force fail logic: Pick a fatal flaw
        flaw = random.choice(['price', 'scandal', 'legal', 'genre'])
        
        genre = random.choice(genres_noise)
        price_val = random.randint(1000, 4500)
        scandal_val = random.choice(["false", "No", "False"])
        legal_val = random.choice(["CLEARED", "WARNING", None])
        
        if flaw == 'price':
            price_val = random.randint(5000, 20000)
            genre = "Random Synth Noise" # Trick genre
        elif flaw == 'scandal':
            scandal_val = random.choice(["true", "Yes", "True"])
            genre = "Shoegaze wannabes" # Trick genre
        elif flaw == 'legal':
            legal_val = "PERMANENT_BAN"
            genre = "Deep Synth" # Trick genre
        # if flaw == 'genre', it stays with a generic genre and doesn't match synth/shoegaze
            
        # Format price erratically
        price_strs = [f"${price_val:,}.00", f"{price_val} USD", f"{price_val}"]
        
        all_bands.append({
            "id": b_id,
            "name": f"Band_{b_id[-4:]}",
            "genre": genre,
            "scandal_raw": scandal_val,
            "legal": legal_val,
            "price_raw": random.choice(price_strs)
        })

    # Add fixed bands
    all_bands.extend(fixed_bands)
    random.shuffle(all_bands)

    # Distribute Data
    finance_rows_q1 = [["Band_ID", "Quoted_Price"]]
    finance_rows_q2 = [["Band_ID", "Quoted_Price"]]
    
    for band in all_bands:
        # 1. Write Submissions (Deep nested JSON)
        region = random.choice(regions)
        month = random.choice(months)
        sub_dir = os.path.join("agency_drop/submissions", f"2023_{region}", month)
        os.makedirs(sub_dir, exist_ok=True)
        
        profile = {
            "band_identifier": band["id"],
            "group_name": band["name"],
            "musical_style": band["genre"],
            "has_recent_scandal": band["scandal_raw"],
            "contact_email": f"contact@{band['name'].replace(' ', '').lower()}.com"
        }
        with open(os.path.join(sub_dir, f"profile_{band['id']}.json"), "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)

        # 2. Write Legal Files (Noisy txt files)
        if band["legal"] is not None:
            legal_txt = f"""# CONFIDENTIAL MEMO
Department: Legal & Compliance
Date: 2023-11-04
Case Officer: J. Doe

BACKGROUND:
We have conducted a thorough background check as per the latest corporate governance protocols.
The following entity has been reviewed under directive 44-B.

Target Band ID: {band['id']}

ANALYSIS:
Extensive social media auditing and public record scraping was performed.
Multiple incidents were reviewed.

CONCLUSION:
Based on the evidence presented to the board...
Final Decision: {band['legal']}

Please update records accordingly.
"""
            with open(os.path.join("agency_drop/legal_archives", f"case_{band['id']}.txt"), "w", encoding="utf-8") as f:
                f.write(legal_txt)
                
        # 3. Distribute to Finance CSVs
        if random.random() > 0.5:
            finance_rows_q1.append([band["id"], band["price_raw"]])
        else:
            finance_rows_q2.append([band["id"], band["price_raw"]])

    # Add pure noise to Legal
    for i in range(50):
        with open(os.path.join("agency_drop/legal_archives", f"draft_policy_{i}.txt"), "w", encoding="utf-8") as f:
            f.write("Just some boring legal drafts without any specific Target Band ID... Final Decision: PENDING")

    # Write Finance CSVs
    with open("agency_drop/finance/quotes_q1.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(finance_rows_q1)
    with open("agency_drop/finance/quotes_q2.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(finance_rows_q2)

if __name__ == "__main__":
    build_env()
