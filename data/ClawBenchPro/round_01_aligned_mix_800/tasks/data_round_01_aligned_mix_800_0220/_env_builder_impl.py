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
    # The agent will use advanced_calorie_calculator_v2 which computes: int((Avg_HR - 50) * Duration * 0.18)
    with open('messy_logs/week1.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'ClassType', 'Duration_mins', 'Avg_HR'])
        writer.writerow(['Alice', 'Spin', '45', '140'])
        writer.writerow(['Bob', 'Yoga', '60', '100'])
        writer.writerow(['Charlie', 'HIIT', '30', '160'])
        writer.writerow(['', 'CorruptedRow', '0', '0']) # Distractor

    # 3. Create messy log 2 (TXT format)
    txt_content = """[David] - 40 mins - HR:150 - Spin
--- corrupted data line ---
[Alice] - 30 mins - HR:150 - Core
[Eve] - 50 mins - HR:120 - Pilates
"""
    with open('messy_logs/week2.txt', 'w') as f:
        f.write(txt_content)

if __name__ == '__main__':
    build_env()
