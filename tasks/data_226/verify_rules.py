import os
import json

def verify():
    report_path = "anomaly_report.json"
    state = {
        "report_exists": False,
        "valid_json": False,
        "correct_keys": False,
        "correct_max_power": False,
        "correct_timestamp": False,
        "extracted_power": None,
        "extracted_timestamp": None
    }
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            if "max_power" in data and "timestamp" in data:
                state["correct_keys"] = True
                state["extracted_power"] = data["max_power"]
                state["extracted_timestamp"] = data["timestamp"]
                
                # Target values injected in env_builder: 850W at 1700000000600
                if data["max_power"] == 850:
                    state["correct_max_power"] = True
                if str(data["timestamp"]) == "1700000000600":
                    state["correct_timestamp"] = True
                    
        except Exception as e:
            pass
            
    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
