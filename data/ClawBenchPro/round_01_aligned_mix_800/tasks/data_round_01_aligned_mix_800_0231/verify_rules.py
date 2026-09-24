import os
import json

def verify():
    report_path = "audit_results/summary.json"
    state = {
        "file_exists": False,
        "valid_json": False,
        "critical_temp_failures_correct": False,
        "green_initiative_failures_correct": False,
        "total_waste_correct": False,
        "used_proper_skill": False
    }

    if os.path.exists(report_path):
        state["file_exists"] = True
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
            state["valid_json"] = True
            
            # Expected values:
            # Temp Fails: B002 (225), B006 (230.1)
            temp_fails = set(data.get("critical_temp_failures", []))
            if temp_fails == {"B002", "B006"}:
                state["critical_temp_failures_correct"] = True
            
            # Green Fails: B004 (5%), B006 (6.25%), B008 (8.3%)
            green_fails = set(data.get("green_initiative_failures", []))
            if green_fails == {"B004", "B006", "B008"}:
                state["green_initiative_failures_correct"] = True
            
            # Waste: B001(50)+B002(60)+B004(100)+B005(50)+B006(50)+B007(10)+B008(100) = 420
            actual_waste = data.get("total_waste_kg", 0)
            if abs(actual_waste - 420) < 0.1:
                state["total_waste_correct"] = True

        except Exception:
            state["valid_json"] = False

    # Check for skill usage in trace (meta-check usually done by verify_prompt, but we can flag here if we parse agent_log)
    # For now, we rely on verify_prompt for trajectory analysis.
    
    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
