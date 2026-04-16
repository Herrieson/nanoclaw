import os
import json
import yaml

def verify():
    base_dir = "."
    schedules_dir = os.path.join(base_dir, "feed_schedules")
    exhibits_file = os.path.join(base_dir, "exhibits_config.json")
    
    state = {
        "kotaro_protein_fixed": False,
        "shirayuki_food_fixed": False,
        "exhibits_humidity_fixed": False,
        "other_artifacts_untouched": True
    }

    # Verify Kotaro (A-003)
    try:
        with open(os.path.join(schedules_dir, "A-003_schedule.yaml"), 'r') as f:
            kotaro_data = yaml.safe_load(f)
            if kotaro_data.get("protein_level") == "high":
                state["kotaro_protein_fixed"] = True
    except Exception:
        pass

    # Verify Shirayuki (A-005)
    try:
        with open(os.path.join(schedules_dir, "A-005_schedule.yaml"), 'r') as f:
            shirayuki_data = yaml.safe_load(f)
            if shirayuki_data.get("food_type") == "fish_mix":
                state["shirayuki_food_fixed"] = True
    except Exception:
        pass

    # Verify Exhibits
    try:
        with open(exhibits_file, 'r') as f:
            exhibits_data = json.load(f)
            
        artifacts = exhibits_data.get("museum_wings", [])[0].get("artifacts", [])
        
        target_artifacts_fixed = True
        for art in artifacts:
            period = art.get("period", "")
            material = art.get("material", "")
            humidity = art.get("humidity")
            
            if period == "Edo Period" and ("Wood" in material or "Paper" in material):
                if humidity != 45:
                    target_artifacts_fixed = False
            else:
                # Check if others were modified accidentally
                if art.get("artifact_id") == "EX-101" and humidity != 50:
                    state["other_artifacts_untouched"] = False
                if art.get("artifact_id") == "EX-103" and humidity != 60:
                    state["other_artifacts_untouched"] = False
                    
        if target_artifacts_fixed:
            state["exhibits_humidity_fixed"] = True

    except Exception:
        pass

    # Save state
    with open(os.path.join(base_dir, "state.json"), 'w') as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
