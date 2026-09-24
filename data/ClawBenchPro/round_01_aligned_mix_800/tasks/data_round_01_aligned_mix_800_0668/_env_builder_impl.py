import os
import csv

def build_env():
    os.makedirs("signups", exist_ok=True)
    
    # Noise files
    with open("signups/rules_draft_v2.txt", "w") as f:
        f.write("Draft rules: 3v3 format. Ages 14-18. Banned weapons: ...")
    with open("signups/junk_log.log", "w") as f:
        f.write("2023-10-12 10:00:01 ERROR: Signup server timeout\n")

    # The actual data file
    roster_data = [
        ["TeamName", "PlayerName", "Age"],
        # Valid Team: Exactly 3 players, all 14-18
        ["Sweat_Lords", "Kyle", "16"],
        ["Sweat_Lords", "Chad", "17"],
        ["Sweat_Lords", "Brad", "18"],
        
        # Valid Team
        ["Aim_Assist", "Sarah", "14"],
        ["Aim_Assist", "John", "15"],
        ["Aim_Assist", "Mike", "16"],
        
        # Invalid Team: Too few players (2)
        ["Duo_Queue", "Alex", "16"],
        ["Duo_Queue", "Sam", "16"],
        
        # Invalid Team: Too many players (4)
        ["Squad_Fam", "Leo", "15"],
        ["Squad_Fam", "Mia", "15"],
        ["Squad_Fam", "Zoe", "15"],
        ["Squad_Fam", "Ian", "15"],
        
        # Invalid Team: Age too high (19)
        ["Boomers", "Dave", "17"],
        ["Boomers", "Rick", "18"],
        ["Boomers", "Morty", "19"],
        
        # Invalid Team: Age too low (13)
        ["Squeakers", "Timmy", "13"],
        ["Squeakers", "Jimmy", "14"],
        ["Squeakers", "Kimmy", "15"]
    ]

    with open("signups/rosters.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(roster_data)

if __name__ == "__main__":
    build_env()
