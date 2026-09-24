import os
import csv

def build_env():
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    csv_data = [
        ["BandName", "Genre", "Quote", "HasScandal"],
        ["Neon Echoes", "Dark Synth-pop", "3500", "False"],
        ["The Crimson Void", "Shoegaze / Dream Pop", "4800", "False"],
        ["Midnight Runners", "Synthwave", "5500", "False"], # Over budget
        ["Static Noise", "Post-punk", "2000", "False"], # Wrong genre
        ["Rebel Yell", "Synth-pop", "4000", "True"], # Scandal
        ["The Blacklisted", "Industrial Synth", "1500", "False"], # On blacklist
        ["Fading Light", "Shoegaze", "3000", "False"],
        ["Pop Sensations", "Pop", "10000", "True"],
        ["Electric Dreams", "Synthpop", "2500", "False"]
    ]

    with open("raw_data/band_submissions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    blacklist_content = """# PR Agency Internal Blacklist
Do not book these bands under any circumstances due to past behavior:
The Blacklisted
Chaos Mongers
Bad PR Band
"""
    with open("raw_data/pr_blacklist.txt", "w", encoding="utf-8") as f:
        f.write(blacklist_content)

if __name__ == "__main__":
    build_env()
