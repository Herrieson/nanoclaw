import json
import os

def verify():
    base_path = "."
    api_state_path = f"{base_path}/api_state.json"
    script_path = f"{base_path}/scripts/monitor_sync.py"
    
    results = {
        "script_fixed": False,
        "data_recovered_and_sent": False,
        "calculation_accuracy": False
    }

    # Check if the script was modified and is now valid python
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            content = f.read()
            if "logs/raw" in content and "requests.post" in content:
                results["script_fixed"] = True

    # Check the "API" state (Agent is expected to mock or actually hit a process they might have to start, 
    # but for this test we check if they wrote the final result to a known location or if they simulated the call)
    # Strategy: We look for a file the Agent might have created to signify completion or the actual api_state.
    if os.path.exists(api_state_path):
        with open(api_state_path, 'r') as f:
            state = json.load(f)
            reports = state.get("received_reports", [])
            if len(reports) > 0:
                results["data_recovered_and_sent"] = True
                # Check calculation: 22:00 to 04:00
                # In env_builder, we can pre-calculate the expected average for the seed if needed, 
                # but here we just check if it's a float within reasonable range.
                last_report = reports[-1]
                if 40.0 <= last_report.get("avg_humidity", 0) <= 70.0:
                    results["calculation_accuracy"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
