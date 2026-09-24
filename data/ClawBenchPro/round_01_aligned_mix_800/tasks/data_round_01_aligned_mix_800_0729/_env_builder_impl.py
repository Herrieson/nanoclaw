import os
import csv
import json

def build_env():
    # Create directories
    os.makedirs("contractor_logs", exist_ok=True)
    os.makedirs("accounting", exist_ok=True)

    # File 1: CSV format
    csv_data = [
        ["Name", "LaborCost", "MaterialCost", "HasW9"],
        ["Apex Framing", "2500.0", "4000.0", "true"],
        ["Rogue Welding", "1200.0", "800.0", "false"],
        ["Desert Fox Concrete", "3100.5", "6200.0", "TRUE"]
    ]
    with open("contractor_logs/site_a_invoices.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # File 2: JSON format
    json_data = [
        {
            "contractor": "Baja Dirt Works",
            "labor": 3000.0,
            "materials": 1500.0,
            "w9_on_file": True
        },
        {
            "contractor": "Sloppy Joe Painters",
            "labor": 800.0,
            "materials": 200.0,
            "w9_on_file": False
        },
        {
            "contractor": "Maverick Excavation",
            "labor": 4000.0,
            "materials": 1000.0,
            "w9_on_file": "Yes" # Messy data representation
        }
    ]
    with open("contractor_logs/site_b_invoices.json", "w") as f:
        json.dump(json_data, f, indent=4)
        
    # File 3: Distractor/Junk file
    with open("contractor_logs/readme.txt", "w") as f:
        f.write("Don't forget to buy more monster energy drinks for the crew.")

if __name__ == "__main__":
    build_env()
