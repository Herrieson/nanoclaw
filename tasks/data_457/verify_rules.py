import os
import json

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "report.json")
    
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "data_match": False,
        "actual_data": None,
        "expected_data": {
            "192.168.1.10": 4,
            "10.0.0.25": 1,
            "172.16.4.8": 3,
            "198.51.100.14": 2
        }
    }
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            state["actual_data"] = data
            
            # Check if actual matches expected exactly
            if data == state["expected_data"]:
                state["data_match"] = True
        except Exception:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
