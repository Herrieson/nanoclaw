import os
import csv

def build_env():
    # Create the directory for the logs
    os.makedirs("logs", exist_ok=True)
    
    # Generate the dirty volunteer dataset
    csv_file_path = os.path.join("logs", "signups.csv")
    
    data = [
        ["Name", "Age", "Committed_Hours", "Brought_Reusable_Bottle", "Notes"],
        ["Alice Trenton", "19", "4", "Yes", "Loves gardening"],
        ["Bobby J", "15", "2", "Yes", "Too young but enthusiastic"],
        ["Charlie Davis", "22", "5", "No", "Forgot bottle, brought plastic"],
        ["Diana Prince", "18", "3", "Yes", "NJ local"],
        ["Evan Wright", "17", "2", "Yes", "Brought metal canteen"],
        ["Fiona Gallagher", "45", "6", "No", "Refused zero-waste pledge"],
        ["Greg House", "50", "4", "YES", "Doctor, likes plants"],
        ["Hannah Abbott", "14", "8", "Yes", "Middle school community service"]
    ]
    
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)

if __name__ == "__main__":
    build_env()
