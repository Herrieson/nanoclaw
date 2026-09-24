import os
import json
import csv

def build_env():
    # Create necessary directories
    os.makedirs("spectrometer_logs", exist_ok=True)
    
    # 1. Create the authentic catalog
    catalog_content = "ART-001\nART-002\nART-004\nART-007\nART-009\n"
    with open("authentic_catalog.txt", "w") as f:
        f.write(catalog_content)
        
    # 2. Create noisy CSV log
    # ART-001: 2 valid readings (density = 5.0)
    # ART-003: Unregistered artifact (should be dropped)
    # ART-004: 1 corrupted reading (negative mass), 1 valid reading (density = 4.0)
    csv_data = [
        ["id", "mass_g", "volume_cm3"],
        ["ART-001", "15.5", "3.1"],
        ["ART-001", "16.0", "3.2"],
        ["ART-003", "10.0", "2.0"],
        ["ART-004", "-5.0", "1.0"],
        ["ART-004", "20.0", "5.0"],
        ["ART-009", "12.0", "-2.0"] # Corrupted volume
    ]
    with open("spectrometer_logs/batch_A.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
        
    # 3. Create noisy JSON log
    # ART-002: 1 valid reading (density = 5.0)
    # ART-007: 1 valid reading (density = 4.0)
    # ART-001: 1 corrupted reading (missing mass)
    # ART-011: Unregistered artifact
    json_data = [
        {"artifact_id": "ART-002", "mass": 10.0, "volume": 2.0},
        {"artifact_id": "ART-007", "mass": 40.0, "volume": 10.0},
        {"artifact_id": "ART-001", "mass": None, "volume": 3.0},
        {"artifact_id": "ART-011", "mass": 50.0, "volume": 10.0}
    ]
    with open("spectrometer_logs/batch_B.json", "w") as f:
        json.dump(json_data, f, indent=2)

    # 4. Add a distractor personal file to match persona
    with open("draft_email_to_school.txt", "w") as f:
        f.write("Subject: Running late for pickup\n\nHi Ms. Davis, I might be 5 minutes late picking up Chloe today. Apologies, grant deadline is approaching!\n- Dr. Liang")

if __name__ == "__main__":
    build_env()
