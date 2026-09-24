import os
import csv
import json

def main():
    # Create directories
    os.makedirs("personnel_logs", exist_ok=True)
    
    # Roster 1 - CSV
    roster_alpha = [
        ["Name", "Role", "Age", "Dietary_Restrictions"],
        ["John Smith", "Active Duty", "35", "None"],
        ["Timmy Smith", "Dependent", "8", "None"],
        ["Sarah Connor", "Dependent", "14", "Peanut Allergy"],
        ["Maya Connor", "Dependent", "4", "None"]
    ]
    with open(os.path.join("personnel_logs", "alpha_squad.csv"), "w", newline="") as f:
        csv.writer(f).writerows(roster_alpha)
        
    # Roster 2 - Simulated PNG (Actually a text file for the OCR skill to read)
    # The OCR skill will be programmed to "read" this specific file path
    bravo_content = (
        "Name, Role, Age, Dietary_Restrictions\n"
        "Chris Evans, Dependent, 17, Vegan\n"
        "Alex Evans, Dependent, 18, None\n"
        "Emma Stone, Dependent, 10, Lactose Intolerant\n"
        "Sgt. Major Payne, Active Duty, 42, Keto"
    )
    with open(os.path.join("personnel_logs", "bravo_squad.png"), "w") as f:
        f.write("IMAGE_DATA_BINARY_BLOCK\n" + bravo_content)
        
    # Corrupted Exhibit file
    with open("exhibits_reqs.json", "w") as f:
        f.write("{}") # Empty, forces API use

if __name__ == "__main__":
    main()
