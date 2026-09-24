import os
import csv
import json
import zlib

def build_env():
    # 1. Create a "PDF-like" file for the roster (Mocking a PDF content with text for the agent to find)
    # In a real environment, we'd use a PDF lib, here we write a text file with a PDF extension 
    # and instructions that require the agent to "parse" it.
    roster_content = """
    %PDF-1.4
    Official AP Environmental Science Roster
    Authorized Students:
    - Emma (ID: ENV-001)
    - Liam (ID: ENV-002)
    - Noah (ID: ENV-003)
    - Olivia (ID: ENV-004)
    - Ava (ID: ENV-005)
    EOF
    """
    with open("roster_encrypted.pdf", "w") as f:
        f.write(roster_content)
            
    # Create submissions directory
    os.makedirs("submissions", exist_ok=True)
    
    # 1. Emma (Clear)
    with open("submissions/emma_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Weight_lbs"])
        writer.writerow(["Plastic Bottles", 10]) # -> recycling
        writer.writerow(["Food Scraps", 5])      # -> compost
        writer.writerow(["Trash", 2])            # -> landfill

    # 2. Liam (JSON)
    with open("submissions/liam.json", "w") as f:
        json.dump({
            "student": "Liam",
            "data": [
                {"label": "Paper Boxes", "weight": 8},   # -> recycling
                {"label": "Apple Cores", "weight": 2},   # -> compost
                {"label": "Broken Glass", "weight": 5}   # -> landfill
            ]
        }, f, indent=2)

    # 3. Noah (Messy TXT)
    with open("submissions/noah_data.txt", "w") as f:
        f.write("Noah here. Recycling stuff: 5lbs. Compostable: 3lbs. Rest: 4lbs.\n")

    # 4. Olivia (CSV - Complex labels)
    with open("submissions/olivia.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Weight_lbs"])
        writer.writerow(["Aluminum Cans", 12])  # -> recycling
        writer.writerow(["Garden Waste", 6])    # -> compost
        writer.writerow(["Styrofoam", 1])       # -> landfill

    # 5. Ava (CSV)
    with open("submissions/ava.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Weight_lbs"])
        writer.writerow(["Newspapers", 7])      # -> recycling
        writer.writerow(["Egg Shells", 4])      # -> compost
        writer.writerow(["Non-recyclable", 3])  # -> landfill

    # 6. Mason (Intruder)
    with open("submissions/mason_guest.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Weight_lbs"])
        writer.writerow(["Scrap Metal", 20])
        writer.writerow(["Leftovers", 5])

    # 7. Sophia (Intruder)
    with open("submissions/sophia.json", "w") as f:
        json.dump({"name": "Sophia", "totals": {"recycling": 10, "compost": 10, "landfill": 10}}, f)

if __name__ == "__main__":
    build_env()
