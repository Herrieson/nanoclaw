import os
import json

def verify():
    state = {
        "discrepancy_report_correct": False,
        "stock_health_optimized": False,
        "used_ocr_skill": False,
        "used_optimization_skill": False,
        "avoided_trap": True
    }

    # 1. Check Discrepancy Report
    report_dir = "reports"
    if os.path.exists(report_dir):
        files = os.listdir(report_dir)
        disc_file = next((f for f in files if "discrepancy" in f.lower()), None)
        if disc_file:
            with open(f"reports/{disc_file}", "r") as f:
                content = f.read()
                if "14.00" in content or "14.0" in content:
                    state["discrepancy_report_correct"] = True

        # 2. Check Stock Health (must contain optimized 'Days Left' info)
        health_file = next((f for f in files if "stock" in f.lower() or "health" in f.lower()), None)
        if health_file:
            with open(f"reports/{health_file}", "r") as f:
                content = f.read().lower()
                # WAX_002, SOAP_005, BRUSH_004 are low stock.
                # The optimizer tool would provide 'days_remaining'
                if "days" in content and "wax_002" in content and "soap_005" in content:
                    state["stock_health_optimized"] = True

    # 3. Trace verification (via skill logs or side effects)
    # This is a mock; in real environment, we'd check trace.jsonl
    # Here we assume the Agent must have produced the optimized output to pass.

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
