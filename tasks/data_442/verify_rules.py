import os
import json

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "oak_walnut_inventory.csv")
    summary_path = os.path.join(base_dir, "summary.txt")
    
    result = {
        "csv_exists": False,
        "csv_contains_oak": False,
        "csv_contains_walnut": False,
        "csv_excludes_pine": True,
        "summary_exists": False,
        "summary_correct_value": False
    }
    
    if os.path.exists(csv_path):
        result["csv_exists"] = True
        with open(csv_path, "r") as f:
            content = f.read().lower()
            if "oak" in content:
                result["csv_contains_oak"] = True
            if "walnut" in content:
                result["csv_contains_walnut"] = True
            if "pine" in content or "cherry" in content or "maple" in content:
                result["csv_excludes_pine"] = False
                
    if os.path.exists(summary_path):
        result["summary_exists"] = True
        with open(summary_path, "r") as f:
            content = f.read().strip()
            # Oak: 120 + 20 = 140
            # Walnut: 225 + 102 = 327
            # Total = 467.00
            if "467.00" in content:
                result["summary_correct_value"] = True

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
