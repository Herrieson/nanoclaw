import os
import json
import re

def verify():
    base_dir = "."
    warning_file = os.path.join(base_dir, "gator_warning.txt")
    
    state = {
        "warning_file_exists": False,
        "day_correct": False,
        "weather_correct": False,
        "extracted_day": None,
        "extracted_weather": None
    }
    
    if os.path.exists(warning_file):
        state["warning_file_exists"] = True
        with open(warning_file, "r") as f:
            content = f.read().lower()
            
            # Extract day
            day_match = re.search(r'day:\s*([a-z]+)', content)
            if day_match:
                day = day_match.group(1)
                state["extracted_day"] = day
                if "thurs" in day:
                    state["day_correct"] = True
                    
            # Extract weather
            weather_match = re.search(r'weather:\s*([a-z]+)', content)
            if weather_match:
                weather = weather_match.group(1)
                state["extracted_weather"] = weather
                if "rain" in weather or "pour" in weather:
                    state["weather_correct"] = True

    with open(os.path.join(base_dir, "state.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
