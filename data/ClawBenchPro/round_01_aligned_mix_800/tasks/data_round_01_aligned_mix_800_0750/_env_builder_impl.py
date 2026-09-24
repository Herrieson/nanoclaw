import os
import csv
import json

def build_env():
    # Create the target directory for field data
    os.makedirs("field_data", exist_ok=True)
    
    # Dataset 1: CSV from older sensors
    # Plot E1 and E2 are compromised (0-2 ladybugs, huge pest numbers)
    csv_data = [
        ["Plot", "Ladybugs", "Pests", "Est_Yield_lbs"],
        ["W1", "150", "10", "5000"],
        ["W2", "120", "15", "4800"],
        ["E1", "2", "800", "1200"],
        ["E2", "0", "950", "900"],
        ["W3", "145", "12", "4200"]
    ]
    
    with open("field_data/sensor_log_A.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
        
    # Dataset 2: JSON from new handhelds
    # Note the different schema/keys and string-formatted numbers. 
    # Plot E3 is compromised.
    json_data = [
        {
            "plot_id": "N1", 
            "beneficial_insects": 200, 
            "pest_index": 5, 
            "projected_yield": "5,500"
        },
        {
            "plot_id": "S1", 
            "beneficial_insects": 180, 
            "pest_index": 20, 
            "projected_yield": "6,000"
        },
        {
            "plot_id": "E3", 
            "beneficial_insects": 1, 
            "pest_index": 700, 
            "projected_yield": "1,100"
        }
    ]
    
    with open("field_data/sensor_log_B.json", "w") as f:
        json.dump(json_data, f, indent=4)
        
    # Distraction data
    with open("field_data/tractor_maintenance.txt", "w") as f:
        f.write("Tractor 4 needs an oil change.\nIrrigation pump on W1 is rattling.\nRemember to buy more organic compost.")

if __name__ == "__main__":
    build_env()
