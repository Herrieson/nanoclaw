import os
import json

def build_env():
    base_dir = "assets/data_318"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "sync_folder"), exist_ok=True)

    # 1. tube_guide.json
    tube_guide = {
        "CBC": "Lavender",
        "CMP": "Gold",
        "PT": "Light Blue",
        "Lactic": "Grey",
        "Lipid": "Tiger Top"
    }
    with open(os.path.join(base_dir, "tube_guide.json"), "w") as f:
        json.dump(tube_guide, f, indent=4)

    # 2. patient_registry.csv
    registry_csv = """ID,Name,DOB
101,Maria G.,1980-05-12
102,John Doe,1992-11-03
103,Sarah T.,1975-08-22
104,Mark W.,2000-01-15
105,Elena R.,1968-07-30
"""
    with open(os.path.join(base_dir, "patient_registry.csv"), "w") as f:
        f.write(registry_csv)

    # 3. barcode_scans.log
    scans_log = """[08:15:22] SYNC START
[08:45:11] SCAN_SUCCESS - UID: BCD-19283 - PATIENT_REF: 101 - STATUS: OK
[09:12:05] SCAN_SUCCESS - UID: BCD-55421 - PATIENT_REF: 102 - STATUS: OK
[10:05:59] SCAN_SUCCESS - UID: BCD-99012 - PATIENT_REF: 103 - STATUS: OK
[11:30:44] SCAN_SUCCESS - UID: BCD-33214 - PATIENT_REF: 104 - STATUS: OK
[12:15:02] SCAN_SUCCESS - UID: BCD-77654 - PATIENT_REF: 105 - STATUS: OK
[12:30:00] SYNC STOP
"""
    with open(os.path.join(base_dir, "barcode_scans.log"), "w") as f:
        f.write(scans_log)

    # 4. shift_notes.txt (Messy data)
    notes = """Man, today is dragging. Can't wait to hit the trails.
First up was Maria G., had to draw a CBC. Finding a vein was annoying.
Then some guy, John Doe, needed a CMP. 
Watched a cool video about falcons during my break.
Sarah T. came in for a PT. 
Mark W. was complaining about the AC, got his Lactic done.
And right before lunch, Elena R. showed up for a Lipid panel. 
Need to buy new hiking boots.
"""
    with open(os.path.join(base_dir, "shift_notes.txt"), "w") as f:
        f.write(notes)

if __name__ == "__main__":
    build_env()
