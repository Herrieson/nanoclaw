import os
import json
import subprocess

def build_env():
    # Install dependencies for LLM Mock Skill
    try:
        subprocess.check_call(["pip", "install", "openai", "httpx"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    os.makedirs("skills/data_round_01_aligned_mix_800_0253", exist_ok=True)

    # 1. Official Roster
    roster = ["Aarav", "Maya", "Leo", "Sam", "Chloe", "Zoe"]
    with open("roster.json", "w", encoding="utf-8") as f:
        json.dump(roster, f)

    # 2. Messy CSV Log (day 1) - Removed ParentSlip column
    csv_content = """Name,Dish,Hours
Aarav,Samosas,3
Leo,Cookies,2
Jake,Brownies,4
Maya,Tikka Masala,5
"""
    with open("logs/day1.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)

    # 3. Messy TXT Log (day 2) - Removed slip mentions
    txt_content = """Volunteer shift notes for Day 2:
Sam worked for 4 hours making Naan.
Chloe worked 1 hour.
Zoe worked for 3 hours.
Aarav worked 2 hours today as well.
"""
    with open("logs/day2.txt", "w", encoding="utf-8") as f:
        f.write(txt_content)

if __name__ == "__main__":
    build_env()
