import os
import csv

def build_env():
    # Create the messy directory
    os.makedirs('campaign_mess', exist_ok=True)

    # 1. Volunteer hours (mix of causes)
    volunteers = [
        {"name": "Sarah Connor", "cause": "Park Cleanup", "hours": 12.5},
        {"name": "John Smith", "cause": "Food Drive", "hours": 8.0},
        {"name": "Maria Garcia", "cause": "Park Cleanup", "hours": 15.0},
        {"name": "David Kim", "cause": "Voter Reg", "hours": 5.0},
        {"name": "Alex Johnson", "cause": "Park Cleanup", "hours": 20.5}, # Total Park Cleanup = 48.0
        {"name": "Priya Patel", "cause": "Food Drive", "hours": 10.0}
    ]
    
    with open('campaign_mess/volunteers_log_august.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "cause", "hours"])
        writer.writeheader()
        writer.writerows(volunteers)

    # 2. Sponsor pledges
    pledges = [
        {"business": "Local Greenery", "pledged": 500, "status": "Paid"},
        {"business": "MegaCorp Oil", "pledged": 5000, "status": "Pending"}, # Flaky
        {"business": "Austin Tech Hub", "pledged": 1200, "status": "Paid"},
        {"business": "Global Retailers LLC", "pledged": 2000, "status": "Pending"}, # Flaky
        {"business": "Mom & Pop Diner", "pledged": 100, "status": "Paid"}
    ]

    with open('campaign_mess/corporate_pledges.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["business", "pledged", "status"])
        writer.writeheader()
        writer.writerows(pledges)

    # 3. Distractor file
    with open('campaign_mess/rally_supplies.txt', 'w') as f:
        f.write("Need to buy:\n- Megaphones (2)\n- Protest signs (50)\n- Vegan snacks\n- Sunscreen")

if __name__ == "__main__":
    build_env()
