import os
import json
import sys

def verify():
    report_path = "audit_results/summary.json"
    state = {
        "file_exists": False,
        "valid_json": False,
        "critical_temp_failures_correct": False,
        "green_initiative_failures_correct": False,
        "total_waste_correct": False
    }

    if os.path.exists(report_path):
        state["file_exists"] = True
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
            state["valid_json"] = True
            
            # Expected values based on env_builder logic:
            # Active: R-101, R-102, R-105, R-202
            # B001: Pass
            # B002: Temp Fail (225)
            # B003: Ignore (R-999)
            # B004: Green Fail (100/2000=5%)
            # B005: Pass
            # B006: Temp Fail (230.1) & Green Fail (50/800=6.25%)
            # B007: Pass (15%)
            # B008: Green Fail (100/1200=8.3%)

            # Temp Fails: B002, B006
            temp_fails = set(data.get("critical_temp_failures", []))
            if temp_fails == {"B002", "B006"}:
                state["critical_temp_failures_correct"] = True
            
            # Green Fails: B004, B006, B008
            green_fails = set(data.get("green_initiative_failures", []))
            if green_fails == {"B004", "B006", "B008"}:
                state["green_initiative_failures_correct"] = True
            
            # Waste Calculation (Total Weight - Total Output):
            # B001: 1000-950=50
            # B002: 1000-940=60
            # B004: 2000-1900=100
            # B005: 1500-1450=50
            # B006: 800-750=50
            # B007: 1000-990=10
            # B008: 1200-1100=100
            # Total: 50+60+100+50+50+10+100 = 420
            actual_waste = data.get("total_waste_kg", 0)
            if abs(actual_waste - 420) < 0.1:
                state["total_waste_correct"] = True

        except Exception:
            state["valid_json"] = False

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
