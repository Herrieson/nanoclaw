import os
import csv

def build_env():
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. Create a dummy PDF file (we'll simulate its content for the skill to "read")
    # In a real scenario, this would be a real PDF. Here it's a placeholder.
    with open("data/vetted_volunteers_list.pdf", "w", encoding="utf-8") as f:
        f.write("%PDF-1.4 (Simulated Scan Content: Alice Smith, Bob Johnson, Charlie Davis, Diana Prince, Eve Adams)")

    # 2. Dirty logs data
    # Logic: 
    # Alice (Active) + Under 5 + 4.5 = 4.5
    # Bob (Active) + Elderly = Ignore
    # Charlie (Active) + Under 5 + 2.5 = 2.5
    # Diana (Expired) + Under 5 = Ignore
    # Eve (Active) + Under 5 + 3.0 = 3.0
    # Frank (Not in list) = Unauthorized
    # Grace (Not in list) = Unauthorized
    # Alice (Active) + Under 5 + 2.0 = 2.0
    # Eve (Active) + Under 5 + invalid = Ignore
    # Henry (Not in list) = Unauthorized
    
    logs_data = [
        ["Name", "Family_Type", "Hours"],
        ["Alice Smith", "Under 5", "4.5"],
        ["Bob Johnson", "Elderly", "3.0"],
        ["Charlie Davis", "Under 5", "2.5"],
        ["Diana Prince", "Under 5", "10.0"], # Will be filtered because Diana is EXPIRED in Skill
        ["Eve Adams", "Under 5", "3.0"],
        ["Frank Castle", "Under 5", "5.0"],
        ["Grace Lee", "Adults", "2.0"],
        ["Alice Smith", "Under 5", "2.0"],
        ["Eve Adams", "Under 5", "null"],
        ["Henry Todd", "Under 5", "1.5"]
    ]
    
    with open("data/logs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(logs_data)

if __name__ == "__main__":
    build_env()
