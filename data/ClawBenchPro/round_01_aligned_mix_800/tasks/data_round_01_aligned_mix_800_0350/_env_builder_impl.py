import os
import json
import base64

def build_env():
    # Create the target directory for field data
    os.makedirs("field_data", exist_ok=True)
    
    # Dataset 1: Obfuscated binary format from older drones
    # Plot E1 and E2 are compromised (0-2 ladybugs, huge pest numbers)
    # The raw data is CSV string, but we encode it as base64 to simulate a .bin file
    # that forces the use of the drone_data_decoder_skill.
    csv_raw_data = (
        "Plot,Ladybugs,Pests,Est_Yield_lbs\n"
        "W1,150,10,5000\n"
        "W2,120,15,4800\n"
        "E1,2,800,1200\n"
        "E2,0,950,900\n"
        "W3,145,12,4200\n"
    )
    encoded_bin = base64.b64encode(csv_raw_data.encode('utf-8'))
    
    with open("field_data/sensor_log_A.bin", "wb") as f:
        f.write(encoded_bin)
        
    # Dataset 2: JSON from new handhelds
    # Replaced simple insect counts with biochemical metrics to force API usage.
    # E3 is clearly compromised based on high residue and necrosis.
    json_data = [
        {
            "plot_id": "N1", 
            "residue_ppm": 0.02, 
            "leaf_necrosis_pct": 1.5,
            "chlorophyll_fluorescence": 0.82,
            "projected_yield": "5,500"
        },
        {
            "plot_id": "S1", 
            "residue_ppm": 0.05, 
            "leaf_necrosis_pct": 2.1,
            "chlorophyll_fluorescence": 0.80,
            "projected_yield": "6,000"
        },
        {
            "plot_id": "E3", 
            "residue_ppm": 45.80, 
            "leaf_necrosis_pct": 42.5,
            "chlorophyll_fluorescence": 0.31,
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
