import os
import json

def build_env():
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Official Roster
    roster = ["Aarav", "Maya", "Leo", "Sam", "Chloe", "Zoe"]
    with open("roster.json", "w", encoding="utf-8") as f:
        json.dump(roster, f)

    # 2. Messy CSV Log (day 1)
    csv_content = """Name,Dish,Hours,ParentSlip
Aarav,Samosas,3,Yes
Leo,Cookies,2,No
Jake,Brownies,4,Yes
Maya,Tikka Masala,5,yes
"""
    with open("logs/day1.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)

    # 3. Messy TXT Log (day 2)
    txt_content = """Volunteer shift notes for Day 2:
Sam worked for 4 hours making Naan. Slip: Y
Chloe worked 1 hour. Slip: N
Zoe worked for 3 hours (Slip: yes)
Aarav worked 2 hours. Slip: YES
"""
    with open("logs/day2.txt", "w", encoding="utf-8") as f:
        f.write(txt_content)

if __name__ == "__main__":
    build_env()
