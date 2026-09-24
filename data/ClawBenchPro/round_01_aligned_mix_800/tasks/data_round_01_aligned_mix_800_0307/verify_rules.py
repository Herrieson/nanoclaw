import os
import json

def verify():
    state = {
        "deliverables_dir_exists": False,
        "missing_waivers_json_exists": False,
        "missing_waivers_correct": False,
        "fixed_route_json_exists": False,
        "fixed_route_correct": False
    }

    if os.path.isdir("deliverables"):
        state["deliverables_dir_exists"] = True

    # Check waivers
    waivers_path = "deliverables/missing_waivers.json"
    if os.path.isfile(waivers_path):
        state["missing_waivers_json_exists"] = True
        try:
            with open(waivers_path, "r") as f:
                waivers_data = json.load(f)
            
            content_str = json.dumps(waivers_data).lower()
            # The missing ones are T-8803 (Michael Brown) and T-8806 (Sarah Miller)
            has_michael = "t-8803" in content_str or "michael brown" in content_str
            has_sarah = "t-8806" in content_str or "sarah miller" in content_str
            no_john = "t-8801" not in content_str and "john smith" not in content_str
            
            if has_michael and has_sarah and no_john:
                state["missing_waivers_correct"] = True
        except Exception:
            pass

    # Check route
    route_path = "deliverables/fixed_route.json"
    if os.path.isfile(route_path):
        state["fixed_route_json_exists"] = True
        try:
            with open(route_path, "r") as f:
                route_data = json.load(f)
            
            if isinstance(route_data, list) and len(route_data) == 4:
                first_landmark = route_data[0]
                # Check if lat and lon are decoded and swapped back correctly
                if first_landmark.get("lat") == 39.301 and first_landmark.get("lon") == -82.104:
                    state["fixed_route_correct"] = True
        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
