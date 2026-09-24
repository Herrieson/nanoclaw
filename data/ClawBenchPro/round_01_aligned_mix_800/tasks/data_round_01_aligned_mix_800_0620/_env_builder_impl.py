import os
import json
import csv

def build_env():
    # Create necessary directories
    os.makedirs('messy_logs', exist_ok=True)
    os.makedirs('client_profiles', exist_ok=True)

    # 1. Create client profiles
    profiles = [
        {"client_name": "Alice", "dietary_restriction": "Kosher", "rsvp_party": True},
        {"client_name": "Bob", "dietary_restriction": "Paleo", "rsvp_party": False},
        {"client_name": "Charlie", "dietary_restriction": "Vegan", "rsvp_party": True},
        {"client_name": "David", "dietary_restriction": "Gluten-Free", "rsvp_party": True},
        {"client_name": "Eve", "dietary_restriction": "Nut Allergy", "rsvp_party": False}
    ]
    with open('client_profiles/profiles.json', 'w') as f:
        json.dump(profiles, f, indent=4)

    # 2. Create messy log 1 (CSV format)
    # Formula: (Avg_HR - 60) * Duration * 0.15
    # Alice: (140-60)*45*0.15 = 80 * 45 * 0.15 = 540
    # Bob: (100-60)*60*0.15 = 40 * 60 * 0.15 = 360
    # Charlie: (160-60)*30*0.15 = 100 * 30 * 0.15 = 450
    with open('messy_logs/week1.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'ClassType', 'Duration_mins', 'Avg_HR'])
        writer.writerow(['Alice', 'Spin', '45', '140'])
        writer.writerow(['Bob', 'Yoga', '60', '100'])
        writer.writerow(['Charlie', 'HIIT', '30', '160'])
        writer.writerow(['', 'CorruptedRow', '0', '0']) # Distractor

    # 3. Create messy log 2 (TXT format)
    # David: (150-60)*40*0.15 = 90 * 40 * 0.15 = 540
    # Alice: (150-60)*30*0.15 = 90 * 30 * 0.15 = 405 (Total Alice = 540 + 405 = 945)
    # Eve: (120-60)*50*0.15 = 60 * 50 * 0.15 = 450
    txt_content = """[David] - 40 mins - HR:150 - Spin
--- corrupted data line ---
[Alice] - 30 mins - HR:150 - Core
[Eve] - 50 mins - HR:120 - Pilates
"""
    with open('messy_logs/week2.txt', 'w') as f:
        f.write(txt_content)

if __name__ == '__main__':
    build_env()
