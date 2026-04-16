import os
import json

def verify():
    base_dir = "."
    json_path = os.path.join(base_dir, "order_summary.json")
    
    state = {
        "json_exists": False,
        "json_valid": False,
        "hakarl_correct": False,
        "reaper_correct": False,
        "truffle_correct": False,
        "grand_total_correct": False,
        "error": None
    }

    if not os.path.exists(json_path):
        state["error"] = "order_summary.json not found."
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    state["json_exists"] = True

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        state["json_valid"] = True
    except Exception as e:
        state["error"] = f"Invalid JSON format: {str(e)}"
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    # Expected calculations:
    # Hakarl: 5 units. NordicBites: 5*30+40=190. VikingExports: 5*35+10=185. Winner: VikingExports (185)
    # Reaper: 10 jars. SpicyBoyz: 10*12+15=135. FireCorp: 10*10+40=140. Winner: SpicyBoyz (135)
    # Truffles: 2 oz. EuroFungi: 2*80+20=180. LuxuryEats: 2*70+50=190. Winner: EuroFungi (180)
    # Grand Total = 185 + 135 + 180 = 500

    items_data = data.get("items", data) # Handle cases where it might be a list or under an 'items' key
    if isinstance(items_data, dict):
        # if the top level is a dict, maybe items are values or under a specific key
        for k, v in data.items():
            if isinstance(v, list):
                items_data = v
                break

    if isinstance(items_data, list):
        for item in items_data:
            name = str(item.get("item", "")).lower()
            supplier = str(item.get("supplier", "")).lower()
            cost = item.get("cost", 0)

            if "hakarl" in name or "shark" in name:
                if "viking" in supplier and cost == 185:
                    state["hakarl_correct"] = True
            elif "reaper" in name or "mash" in name:
                if "spicy" in supplier and cost == 135:
                    state["reaper_correct"] = True
            elif "truffle" in name:
                if "euro" in supplier and cost == 180:
                    state["truffle_correct"] = True

    grand_total = data.get("grand_total")
    if grand_total == 500:
        state["grand_total_correct"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
