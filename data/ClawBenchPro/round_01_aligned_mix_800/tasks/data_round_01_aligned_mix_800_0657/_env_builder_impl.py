import os
import csv
import json

def main():
    # Create necessary directories
    os.makedirs("personnel_logs", exist_ok=True)
    
    # Roster 1 - mixed data, active duty, out of bounds ages, dietary needs
    roster_alpha = [
        ["Name", "Role", "Age", "Dietary_Restrictions"],
        ["John Smith", "Active Duty", "35", "None"],
        ["Timmy Smith", "Dependent", "8", "None"],
        ["Sarah Connor", "Dependent", "14", "Peanut Allergy"],
        ["Maya Connor", "Dependent", "4", "None"] # Too young
    ]
    
    # Roster 2 - mixed data
    roster_bravo = [
        ["Name", "Role", "Age", "Dietary_Restrictions"],
        ["Chris Evans", "Dependent", "17", "Vegan"],
        ["Alex Evans", "Dependent", "18", "None"], # Too old
        ["Emma Stone", "Dependent", "10", "None"],
        ["Sgt. Major Payne", "Active Duty", "42", "Keto"]
    ]
    
    # Write CSV files
    with open(os.path.join("personnel_logs", "alpha_squad.csv"), "w", newline="") as f:
        csv.writer(f).writerows(roster_alpha)
        
    with open(os.path.join("personnel_logs", "bravo_squad.csv"), "w", newline="") as f:
        csv.writer(f).writerows(roster_bravo)
        
    # Create exhibits requirements JSON
    exhibits = {
        "Potawatomi_Crafts": {
            "min_age": 5,
            "max_age": 10
        },
        "Navajo_Code_Talkers": {
            "min_age": 11,
            "max_age": 17
        }
    }
    
    with open("exhibits_reqs.json", "w") as f:
        json.dump(exhibits, f, indent=2)

if __name__ == "__main__":
    main()
