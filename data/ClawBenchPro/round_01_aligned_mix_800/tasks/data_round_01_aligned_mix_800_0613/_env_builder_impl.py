import os
import json
import csv

def build_env():
    roster_content = """Sarah Jenkins
Michael Chang
Emily Davis
David Rodriguez
Chloe Dubois"""
    
    with open("roster.txt", "w", encoding="utf-8") as f:
        f.write(roster_content)

    os.makedirs("records", exist_ok=True)

    site_a_data = [
        {"volunteer_name": "Sarah Jenkins", "logged_hours": 4.0},
        {"volunteer_name": "Gary Smith", "logged_hours": 2.0},
        {"volunteer_name": "Chloe Dubois", "logged_hours": 1.5}
    ]
    with open("records/site_a_log.json", "w", encoding="utf-8") as f:
        json.dump(site_a_data, f, indent=4)

    with open("records/site_b_log.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Duration"])
        writer.writerow(["Michael Chang", "3.5"])
        writer.writerow(["Emily Davis", "4.0"])
        writer.writerow(["Melissa Vance", "1.5"])

    site_c_data = """david rodriguez : 2 hours
Chloe Dubois : 3.5 hrs
gary smith: 1 hour
"""
    with open("records/site_c_log.txt", "w", encoding="utf-8") as f:
        f.write(site_c_data)

if __name__ == "__main__":
    build_env()
