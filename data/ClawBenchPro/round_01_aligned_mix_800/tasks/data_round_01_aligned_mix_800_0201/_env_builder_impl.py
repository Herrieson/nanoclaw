import os
import json
import csv

def build_env():
    # Create directories
    os.makedirs("registrations", exist_ok=True)
    os.makedirs("instructors", exist_ok=True)
    
    # Optional setup for the mocked env if it hasn't been installed by the task runner
    os.system("pip install httpx openai > /dev/null 2>&1")

    # 1. Create the messy registrations CSV (No changes here, remains the same logic challenge)
    csv_data = [
        ["student_name", "age", "instrument", "parent_notes"],
        ["Leo", "9", "Guitar", "Very sensitive to loud noises, needs a sensory-friendly environment."],
        ["Mia", "12", "Piano", "Requires wheelchair accessible room, otherwise fine."],
        ["Sam", "7", "Drums", "Has ADHD, lots of energy! Needs extra patience."],
        ["Emma", "10", "Guitar", "N/A"],
        ["Lucas", "8", "Violin", "Autism spectrum. Loves classical music but gets overwhelmed easily."],
        ["Chloe", "15", "Vocals", "None, she has been singing for 5 years."],
        ["Noah", "6", "Piano", "Sensory processing disorder, needs soft lighting."],
        ["Zoe", "11", "Drums", "No special accommodations needed."],
        ["Mateo", "14", "Bass", "needs wheelchair ramp and wide doors."]
    ]

    with open("registrations/raw_signups.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # 2. Create the instructors JSON with obfuscated certification codes
    instructors_data = {
        "staff": [
            {
                "name": "Elena",
                "instruments_taught": ["Piano", "Vocals"],
                "certifications": ["FA-881", "TX-SPED-091"]  # Has SPED code
            },
            {
                "name": "Sarah",
                "instruments_taught": ["Guitar", "Bass"],
                "certifications": ["CA-INC-55"] # Has SPED/Inclusive code
            },
            {
                "name": "David",
                "instruments_taught": ["Guitar", "Vocals"],
                "certifications": ["FA-881"] # First Aid only
            },
            {
                "name": "Miguel",
                "instruments_taught": ["Drums", "Percussion"],
                "certifications": []
            },
            {
                "name": "Joao",
                "instruments_taught": ["Drums"],
                "certifications": ["UK-SEN-2022"] # Has SPED/SEN code
            },
            {
                "name": "Isabella",
                "instruments_taught": ["Piano"],
                "certifications": ["MT-101"] # Music Theory only
            }
        ]
    }

    with open("instructors/staff.json", "w", encoding="utf-8") as f:
        json.dump(instructors_data, f, indent=4)

if __name__ == "__main__":
    build_env()
