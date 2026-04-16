import os
import json

def verify():
    base_dir = "."
    summary_path = os.path.join(base_dir, "summary.json")
    
    result = {
        "summary_exists": False,
        "has_correct_keys": False,
        "materials_correct": False,
        "coords_correct": False,
        "total_correct": False,
        "score": 0
    }

    if not os.path.exists(summary_path):
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    result["summary_exists"] = True

    try:
        with open(summary_path, "r") as f:
            data = json.load(f)
    except Exception:
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    required_keys = {"table_materials", "badger_trail_coords", "unpaid_total"}
    if required_keys.issubset(data.keys()):
        result["has_correct_keys"] = True

    # Check materials (loose checking, just ensure the main items are there)
    materials = data.get("table_materials", [])
    if isinstance(materials, list) and len(materials) >= 4:
        mat_str = " ".join(materials).lower()
        if "cherry" in mat_str and "glue" in mat_str and "screws" in mat_str and "polyurethane" in mat_str:
            result["materials_correct"] = True
            result["score"] += 30

    # Check coords
    coords = data.get("badger_trail_coords", "")
    if isinstance(coords, str) and "42.6321,-89.6543" in coords:
        result["coords_correct"] = True
        result["score"] += 30

    # Check total (3250.75 + 1200.25 + 800.00 = 5251.00)
    total = data.get("unpaid_total", 0)
    try:
        if abs(float(total) - 5251.00) < 0.01:
            result["total_correct"] = True
            result["score"] += 40
    except (ValueError, TypeError):
        pass

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
