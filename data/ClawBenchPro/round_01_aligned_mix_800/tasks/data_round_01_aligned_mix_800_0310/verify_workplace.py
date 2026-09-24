import os
import json
import math

def extract_all_values(obj):
    values = []
    if isinstance(obj, dict):
        for v in obj.values():
            values.extend(extract_all_values(v))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(extract_all_values(item))
    else:
        values.append(obj)
    return values

def verify():
    state = {
        "deliverable_exists": False,
        "json_format_valid": False,
        "closed_branches_removed": False,
        "math_calculated_perfectly": False
    }

    file_path = "workspace/q3_forecast_summary.json"
    if not os.path.exists(file_path):
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f)
        return

    state["deliverable_exists"] = True

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content_str = f.read()
            data = json.loads(content_str)
        state["json_format_valid"] = True
    except Exception:
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f)
        return

    # Check if the closed branch (103 - Old Tavern Brooklyn) was successfully excluded
    if "103" not in content_str and "Old Tavern" not in content_str:
        state["closed_branches_removed"] = True

    all_vals = extract_all_values(data)
    numeric_vals = [v for v in all_vals if isinstance(v, (int, float))]

    # Expected Q3 USD projections (Rates mandated via internal DB mock):
    # 101: EUR 100k, 120k -> USD 110k, 132k -> Avg 121k -> +5% = 127050
    # 102: GBP 80k, 90k -> USD 100k, 112.5k -> Avg 106.25k -> +5% = 111562.5
    # 104: EUR 50k, 48k -> USD 55k, 52.8k -> Avg 53.9k -> +5% = 56595
    # 105: USD 150k, 160k -> USD 150k, 160k -> Avg 155k -> +5% = 162750
    # 106: JPY 5m, 6m -> USD 35k, 42k -> Avg 38.5k -> +5% = 40425
    expected_values = [127050.0, 111562.5, 56595.0, 162750.0, 40425.0]

    matches = 0
    for exp in expected_values:
        for nv in numeric_vals:
            if math.isclose(exp, nv, rel_tol=1e-3):
                matches += 1
                break

    if matches == len(expected_values):
        state["math_calculated_perfectly"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
