import os
import json

def verify():
    state = {
        "solar_folder_created": False,
        "water_folder_created": False,
        "solar_files_moved": False,
        "water_files_moved": False,
        "json_feed_exists": False,
        "json_feed_valid": False,
        "correct_solar_total": False,
        "correct_water_total": False,
        "noise_files_untouched": False
    }

    # Verify directory structures
    if os.path.isdir("organized/solar_logs"):
        state["solar_folder_created"] = True
        if os.path.exists("organized/solar_logs/solar_january.csv") and os.path.exists("organized/solar_logs/solar_february.csv"):
            state["solar_files_moved"] = True

    if os.path.isdir("organized/water_logs"):
        state["water_folder_created"] = True
        if os.path.exists("organized/water_logs/water_sensor_front.json") and os.path.exists("organized/water_logs/water_sensor_back.json"):
            state["water_files_moved"] = True

    # Verify noise files were left alone
    if os.path.exists("gadget_dumps/grocery_receipt.txt") and os.path.exists("gadget_dumps/tech_news_article.txt"):
        state["noise_files_untouched"] = True

    # Verify output JSON
    if os.path.exists("smart_display_feed.json"):
        state["json_feed_exists"] = True
        try:
            with open("smart_display_feed.json", "r") as f:
                data = json.load(f)
                state["json_feed_valid"] = True
                
                # We expect total_solar_kwh = 100, total_water_gallons = 200
                if data.get("total_solar_kwh") == 100:
                    state["correct_solar_total"] = True
                if data.get("total_water_gallons") == 200:
                    state["correct_water_total"] = True
        except Exception:
            pass

    # Save physical state probes
    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
