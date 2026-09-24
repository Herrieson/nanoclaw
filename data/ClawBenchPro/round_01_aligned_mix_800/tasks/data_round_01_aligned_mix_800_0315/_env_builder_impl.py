import os
import json
import csv

def build_env():
    # Create necessary directories
    os.makedirs("spectrometer_logs", exist_ok=True)
    os.makedirs("grant_submission", exist_ok=True)
    
    # 1. Create the authentic catalog as a "PDF" (Simulated by a file with PDF header)
    # Artifacts: ART-001, ART-002, ART-005, ART-008
    catalog_text = "OFFICIAL RESEARCH CATALOG - DR. LIANG\nCONFIDENTIAL\nLISTED IDS:\n- ART-001 (Pallasite)\n- ART-002 (Iron-Nickel)\n- ART-005 (Chondrite)\n- ART-008 (Mesosiderite)\nEND OF FILE"
    with open("official_catalog_confidential.pdf", "w") as f:
        f.write("%PDF-1.4\n")  # Mock PDF header
        f.write(catalog_text)
        
    # 2. Batch A (CSV): ART-001 (Valid), ART-003 (Fake), ART-005 (Corrupted)
    csv_data = [
        ["id", "mass_g", "volume_cm3"],
        ["ART-001", "15.0", "3.0"],   # Density 5.0
        ["ART-003", "10.0", "2.0"],   # Not in catalog
        ["ART-005", "-50.0", "10.0"], # Corrupted
        ["ART-005", "40.0", "8.0"]    # Valid, Density 5.0
    ]
    with open("spectrometer_logs/batch_A.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
        
    # 3. Batch B (JSON): ART-002 (Valid), ART-008 (Valid), ART-001 (Missing Data)
    json_data = [
        {"artifact_id": "ART-002", "mass": 20.0, "volume": 4.0}, # Density 5.0
        {"artifact_id": "ART-008", "mass": 36.0, "volume": 9.0}, # Density 4.0
        {"artifact_id": "ART-001", "mass": None, "volume": 3.0}  # Corrupted
    ]
    with open("spectrometer_logs/batch_B.json", "w") as f:
        json.dump(json_data, f, indent=2)

    # 4. Batch C (RAW/TXT): ART-008 (Valid extra reading)
    with open("spectrometer_logs/batch_C.raw", "w") as f:
        f.write("REC|ART-008|MASS:44.0|VOL:11.0|END\n") # Density 4.0

    # 5. Distractor
    with open("urgent_note.txt", "w") as f:
        f.write("Don't forget to check the purity validator for the grant report! Raw density is NOT enough.")

if __name__ == "__main__":
    build_env()
