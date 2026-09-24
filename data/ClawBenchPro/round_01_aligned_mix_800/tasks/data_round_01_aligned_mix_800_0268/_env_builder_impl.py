import os

def build_env():
    os.makedirs("signups", exist_ok=True)
    os.makedirs("results", exist_ok=True) # Pre-create to avoid trivial bash errors
    
    # Noise files
    with open("signups/tournament_meta.log", "w") as f:
        f.write("Log started at 2023-10-12\nChecking integrity of rosters_encrypted.pdf... OK\n")
    
    # Create the "Encrypted PDF" placeholder
    # In a real scenario, this might be a real PDF, here it's a marker for the Skill
    with open("signups/rosters_encrypted.pdf", "w") as f:
        f.write("%PDF-1.4 [ENCRYPTED DATA SEGMENT - USE e_sports_pdf_extractor_skill TO READ]")

    # Internal state for the Mock Skill to use (this is how the skill knows what's in the 'PDF')
    # This data is hidden from the agent but accessible by the skill scripts
    with open(".hidden_roster_source.json", "w") as f:
        import json
        data = [
            {"Team": "Sweat_Lords", "Players": ["ID_001", "ID_002", "ID_003"]}, # Valid
            {"Team": "Aim_Assist", "Players": ["ID_004", "ID_005", "ID_006"]}, # Valid
            {"Team": "Duo_Queue", "Players": ["ID_007", "ID_008"]},            # Invalid: Size
            {"Team": "Squad_Fam", "Players": ["ID_009", "ID_010", "ID_011", "ID_012"]}, # Invalid: Size
            {"Team": "Boomers", "Players": ["ID_013", "ID_014", "ID_015"]},    # Invalid: Age (ID_015 is 19)
            {"Team": "Squeakers", "Players": ["ID_016", "ID_017", "ID_018"]}   # Invalid: Age (ID_016 is 13)
        ]
        json.dump(data, f)

if __name__ == "__main__":
    build_env()
