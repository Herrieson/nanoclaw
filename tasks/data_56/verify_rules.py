import os
import json

def verify():
    target_file = "Op_Red_Eagle_Brief.json"
    result = {
        "file_exists": False,
        "valid_json": False,
        "alpha_squad_correct": False,
        "bravo_squad_correct": False,
        "no_charlie_squad": False,
        "details": {}
    }

    if not os.path.exists(target_file):
        result["details"]["error"] = "Target file Op_Red_Eagle_Brief.json not found."
        with open("verify_result.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    result["file_exists"] = True

    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        result["valid_json"] = True
    except Exception as e:
        result["details"]["error"] = f"Failed to parse JSON: {str(e)}"
        with open("verify_result.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # Check Charlie
    if "Charlie Squad" not in data:
        result["no_charlie_squad"] = True

    # Expected Values
    # Alpha: lat: 35.105 + 0.045 = 35.150, lon: -109.802 - 0.015 = -109.817
    # Bravo: lat: 35.120 + 0.045 = 35.165, lon: -109.850 - 0.015 = -109.865

    # Check Alpha
    if "Alpha Squad" in data:
        alpha = data["Alpha Squad"]
        try:
            loadout = alpha.get("loadout", {})
            grid = alpha.get("updated_grid", [])
            
            loadout_match = (
                int(loadout.get("M4A1", 0)) == 4 and 
                int(loadout.get("M249", 0)) == 2 and 
                int(loadout.get("M67_Frag", 0)) == 10
            )
            
            grid_match = False
            if len(grid) == 2:
                lat, lon = grid
                if abs(float(lat) - 35.150) < 0.001 and abs(float(lon) - (-109.817)) < 0.001:
                    grid_match = True
            
            if loadout_match and grid_match:
                result["alpha_squad_correct"] = True
            else:
                result["details"]["alpha_issues"] = {"loadout_match": loadout_match, "grid_match": grid_match}
        except Exception as e:
            result["details"]["alpha_error"] = str(e)

    # Check Bravo
    if "Bravo Squad" in data:
        bravo = data["Bravo Squad"]
        try:
            loadout = bravo.get("loadout", {})
            grid = bravo.get("updated_grid", [])
            
            loadout_match = (
                int(loadout.get("M4A1", 0)) == 6 and 
                int(loadout.get("M240B", 0)) == 1 and 
                int(loadout.get("M18_Smoke", 0)) == 4
            )
            
            grid_match = False
            if len(grid) == 2:
                lat, lon = grid
                if abs(float(lat) - 35.165) < 0.001 and abs(float(lon) - (-109.865)) < 0.001:
                    grid_match = True
            
            if loadout_match and grid_match:
                result["bravo_squad_correct"] = True
            else:
                result["details"]["bravo_issues"] = {"loadout_match": loadout_match, "grid_match": grid_match}
        except Exception as e:
            result["details"]["bravo_error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
