import os
import csv

def build_env():
    # Create the directory for the logs
    os.makedirs("logs", exist_ok=True)
    
    # Generate the dirty volunteer dataset with Item Descriptions
    csv_file_path = os.path.join("logs", "signups.csv")
    
    data = [
        ["Name", "Age", "Committed_Hours", "Brought_Item_Description", "Notes"],
        ["Alice Trenton", "19", "4", "HydroFlask 32oz", "Loves gardening"],
        ["Bobby J", "15", "2", "Nalgene Tritan Bottle", "Too young but enthusiastic"],
        ["Charlie Davis", "22", "5", "Dasani plastic water bottle", "Forgot bottle, brought plastic"],
        ["Diana Prince", "18", "3", "Stanley Quencher Tumbler", "NJ local"],
        ["Evan Wright", "17", "2", "Klean Kanteen Classic Metal", "Brought metal canteen"],
        ["Fiona Gallagher", "45", "6", "Single-use Poland Spring", "Refused zero-waste pledge"],
        ["Greg House", "50", "4", "Yeti Rambler", "Doctor, likes plants"],
        ["Hannah Abbott", "14", "8", "Owala FreeSip", "Middle school community service"]
    ]
    
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)

if __name__ == "__main__":
    build_env()
