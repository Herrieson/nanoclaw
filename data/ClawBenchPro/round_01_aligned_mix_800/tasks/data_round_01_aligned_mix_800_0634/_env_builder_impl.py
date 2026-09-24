import os
import csv
import random

def build_env():
    # Create the raw_inventory directory
    os.makedirs("raw_inventory", exist_ok=True)
    
    # Sample data for comic books
    comics_data_1 = [
        ["Title", "Issue", "Condition_Score", "Market_Value"],
        ["The Amazing Spider-Man", "129", "9.2", "2500"],
        ["X-Men", "1", "4.5", "12000"], # Low condition
        ["Batman", "181", "8.0", "1500"],
        ["Fantastic Four", "48", "7.5", ""], # Missing value
        ["The Avengers", "4", "9.0", "3000"],
    ]
    
    comics_data_2 = [
        ["Title", "Issue", "Condition_Score", "Market_Value"],
        ["The Amazing Spider-Man", "129", "8.5", "2000"], # Duplicate, lower score
        ["Iron Man", "1", "9.6", "5000"],
        ["Green Lantern", "76", "9.4", "800"],
        ["X-Men", "101", "5.5", "600"], # Low condition
        ["Action Comics", "252", "7.0", "4500"],
    ]

    # Create messy CSV files
    with open("raw_inventory/box_alpha.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(comics_data_1)
        
    with open("raw_inventory/shelf_beta.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(comics_data_2)

    # Add a decoy file
    with open("raw_inventory/notes.txt", "w") as f:
        f.write("Need to check the attic for more Spider-Man issues.")

if __name__ == "__main__":
    build_env()
