import os
import json
import sys

def verify():
    state = {
        "export_dir_exists": False,
        "report_file_exists": False,
        "is_valid_json": False,
        "has_correct_keys": False,
        "peak_load_correct": False,
        "peak_sensor_correct": False,
        "flagged_sensors_correct": False
    }

    if os.path.isdir("export"):
        state["export_dir_exists"] = True

    report_path = "export/stress_report.json"
    if os.path.isfile(report_path):
        state["report_file_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # Convert keys to lowercase string representations for fuzzy matching
            keys_str = str(data.keys()).lower()
            
            # Check for conceptual keys based on prompt
            has_peak = "load" in keys_str or "max" in keys_str or "peak" in keys_str
            has_sensor = "transducer" in keys_str or "sensor" in keys_str or "id" in keys_str
            has_flagged = "flag" in keys_str or "breach" in keys_str or "tolerance" in keys_str
            
            if has_peak and has_sensor and has_flagged:
                state["has_correct_keys"] = True

            # Extract values based on likely key names
            peak_val = None
            peak_sensor = None
            flagged_list = []

            for k, v in data.items():
                k_low = k.lower()
                if "load" in k_low or "max" in k_low or "peak" in k_low:
                    if isinstance(v, (int, float)):
                        peak_val = float(v)
                if ("sensor" in k_low or "transducer" in k_low or "id" in k_low) and not isinstance(v, list):
                    peak_sensor = v
                if isinstance(v, list):
                    flagged_list = v

            if peak_val == 1250.75:
                state["peak_load_correct"] = True
            
            if peak_sensor == "TX-007":
                state["peak_sensor_correct"] = True

            # Check if flagged sensors contain exactly TX-004 and TX-009
            if isinstance(flagged_list, list) and len(flagged_list) == 2:
                if set(flagged_list) == {"TX-004", "TX-009"}:
                    state["flagged_sensors_correct"] = True

        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
