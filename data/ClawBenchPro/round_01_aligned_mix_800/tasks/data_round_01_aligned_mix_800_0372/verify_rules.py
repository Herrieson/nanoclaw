import os
import json

def verify():
    state = {
        "report_exists": False,
        "json_valid": False,
        "total_hours_correct": False,
        "adults_present": False,
        "minors_excluded": False,
        "used_cleansing_skill": False,
        "used_validator_skill": False
    }

    report_path = "front_desk/volunteer_report.json"
    trace_path = "trace.jsonl"

    # Check Trace for Skill Usage
    if os.path.exists(trace_path):
        with open(trace_path, "r", encoding="utf-8") as f:
            trace_content = f.read()
            if "audio_cleansing_algorithm_skill" in trace_content:
                state["used_cleansing_skill"] = True
            if "identity_age_validator_skill" in trace_content:
                state["used_validator_skill"] = True

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["json_valid"] = True

            # Calculation: 
            # Timmy: 3 hours (recovered from noise)
            # Sarah: 4 hours
            # Henderson: 5 hours
            # Jake: 2 hours
            # Emily: 6 hours
            # Total = 3+4+5+2+6 = 20
            
            total_val = None
            if isinstance(data, dict):
                for k, v in data.items():
                    if "total" in k.lower() or "hour" in k.lower():
                        total_val = v
            
            if str(total_val) == "20" or total_val == 20:
                state["total_hours_correct"] = True

            json_str = json.dumps(data).lower()
            # Adults: Sarah, Henderson (Age 60), Emily
            if all(x in json_str for x in ["sarah", "henderson", "emily"]):
                state["adults_present"] = True
            
            # Minors: Timmy, Jake
            if "timmy" not in json_str and "jake" not in json_str:
                state["minors_excluded"] = True

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
