import os
import csv

def build_env():
    # Create the directories
    os.makedirs("raw_inventory", exist_ok=True)
    
    # 1. Box Alpha: Standard but some missing values
    box_alpha = [
        ["Title", "Issue", "Condition_Score", "Market_Value"],
        ["The Amazing Spider-Man", "129", "9.2", "2500"],
        ["X-Men", "1", "4.5", "12000"], 
        ["Batman", "181", "8.0", "1500"],
        ["Fantastic Four", "48", "9.0", "PENDING"], # Must use tool
    ]
    
    # 2. Shelf Beta: Messy grades
    shelf_beta = [
        ["Title", "Issue", "Condition_Score", "Market_Value"],
        ["The Amazing Spider-Man", "129", "NM 9.4", "2800"], # Duplicate, needs validation
        ["Iron Man", "1", "9.6", "5000"],
        ["Green Lantern", "76", "VF 8.0", "800"], # Needs conversion
        ["X-Men", "101", "5.5", "600"],
    ]

    with open("raw_inventory/box_alpha.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(box_alpha)
        
    with open("raw_inventory/shelf_beta.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(shelf_beta)

    # 3. PDF Placeholder (Simulated via a text file that the agent must "read" using a skill)
    with open("raw_inventory/vault_index.pdf", "w") as f:
        f.write("[SECURE DOCUMENT]\nItem: The Avengers #4\nGrade: Mint 9.0\nValue: 3000\nStatus: Vaulted")

    # Add notes
    with open("raw_inventory/README.txt", "w") as f:
        f.write("Note: Use the professional grading skill for any non-numeric scores in shelf_beta.")

if __name__ == "__main__":
    build_env()
