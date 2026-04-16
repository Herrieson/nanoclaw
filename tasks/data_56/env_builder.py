import os
import json

def build_env():
    base_dir = "assets/data_56"
    os.makedirs(base_dir, exist_ok=True)

    intel_content = """[0800 HRS] COMMAND: Initiating Operation Red Eagle. AO is sector 7G, near Navajo Nation borders.
[0815 HRS] SITREP: Alpha Squad loadout confirmed at armory. Issued: 4x M4A1, 2x M249, 10x M67_Frag. Initial rally point grid coordinates: 35.105, -109.802.
[0845 HRS] SITREP: Charlie Squad moving to flank. Issued: 5x M4A1. Grid: 35.200, -109.700. (Disregard, not in main push).
[0900 HRS] SITREP: Bravo Squad ready for tactical insertion. Loadout: 6x M4A1, 1x M240B, 4x M18_Smoke. Initial rally point grid coordinates: 35.120, -109.850.
[0930 HRS] LOGISTICS: Munitions low, expect delay on resupply."""
    
    with open(os.path.join(base_dir, "logistics_intel.txt"), "w") as f:
        f.write(intel_content)

    offset_data = {
        "encryption_key": "NAVAJO_WIND",
        "lat_shift": 0.045,
        "lon_shift": -0.015,
        "note": "Apply these shifts to all raw rally grids before deployment to compensate for localized magnetic anomalies."
    }
    
    with open(os.path.join(base_dir, "nav_offset.json"), "w") as f:
        json.dump(offset_data, f, indent=2)

if __name__ == "__main__":
    build_env()
