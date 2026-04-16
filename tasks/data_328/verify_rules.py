import os
import json

def verify():
    base_dir = "."
    summary_path = os.path.join(base_dir, "financial_summary.json")
    
    state = {
        "file_exists": False,
        "json_valid": False,
        "schema_correct": False,
        "patient_revenue_accurate": False,
        "total_patient_revenue_correct": False,
        "painting_expenses_accurate": False,
        "total_painting_expenses_correct": False,
        "michael_vance_excluded": False
    }

    if not os.path.exists(summary_path):
        with open(os.path.join(base_dir, "state.json"), "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True

    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        state["json_valid"] = True
    except json.JSONDecodeError:
        with open(os.path.join(base_dir, "state.json"), "w") as f:
            json.dump(state, f)
        return

    # Check Schema
    required_keys = {"patient_revenue", "total_patient_revenue", "painting_expenses", "total_painting_expenses"}
    if required_keys.issubset(data.keys()):
        state["schema_correct"] = True

        # Check total patient revenue (Alice 150 + David 80 + Sarah 80 + Elena 150 = 460)
        # Michael Vance cancelled, so he shouldn't be in the revenue
        try:
            total_patient = float(data.get("total_patient_revenue", 0))
            if abs(total_patient - 460.0) < 0.01:
                state["total_patient_revenue_correct"] = True
            
            # Check individual patients
            patients = data.get("patient_revenue", {})
            if "Michael Vance" not in patients:
                state["michael_vance_excluded"] = True
            
            if patients.get("Alice Carter") in [150, 150.0] and \
               patients.get("David Lee") in [80, 80.0] and \
               patients.get("Sarah Jenkins") in [80, 80.0] and \
               patients.get("Elena Rostova") in [150, 150.0]:
                state["patient_revenue_accurate"] = True

            # Check total painting expenses (Oils 65 + Canvas 110 + Brushes 32.50 = 207.50)
            total_painting = float(data.get("total_painting_expenses", 0))
            if abs(total_painting - 207.50) < 0.01:
                state["total_painting_expenses_correct"] = True

            # Just checking if there are 3 painting items roughly matching
            painting_items = data.get("painting_expenses", {})
            if len(painting_items.keys()) >= 3:
                state["painting_expenses_accurate"] = True

        except Exception:
            pass

    with open(os.path.join(base_dir, "state.json"), "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
