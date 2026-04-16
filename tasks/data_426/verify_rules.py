import os
import csv
import json

def verify():
    base_dir = "."
    bom_path = os.path.join(base_dir, "bom.csv")
    ti_path = os.path.join(base_dir, "titanium_parts.txt")
    
    result = {
        "bom_exists": False,
        "bom_header_correct": False,
        "bom_row_count": 0,
        "bom_defaults_handled": False,
        "ti_exists": False,
        "ti_parts_correct": False,
        "ti_parts_found": []
    }

    # Verify BOM
    if os.path.exists(bom_path):
        result["bom_exists"] = True
        try:
            with open(bom_path, "r") as f:
                reader = csv.reader(f)
                rows = list(reader)
                if len(rows) > 0:
                    header = rows[0]
                    if [h.strip().lower() for h in header] == ['part id', 'material', 'weight']:
                        result["bom_header_correct"] = True
                
                result["bom_row_count"] = len(rows) - 1 if len(rows) > 0 else 0
                
                # Check defaults
                defaults_handled_correctly = True
                for row in rows[1:]:
                    if len(row) == 3:
                        pid, mat, wt = row
                        if pid == "WS-303" and str(wt) != "0":
                            defaults_handled_correctly = False
                        if pid == "ER-404" and mat != "Unknown":
                            defaults_handled_correctly = False
                        if pid == "VD-808" and (mat != "Unknown" or str(wt) != "0"):
                            defaults_handled_correctly = False
                result["bom_defaults_handled"] = defaults_handled_correctly
        except Exception:
            pass

    # Verify Titanium parts
    expected_ti_parts = {"LG-202", "EN-505", "FL-707"}
    if os.path.exists(ti_path):
        result["ti_exists"] = True
        try:
            with open(ti_path, "r") as f:
                content = f.read().splitlines()
                parts = [p.strip() for p in content if p.strip()]
                result["ti_parts_found"] = parts
                
                if set(parts) == expected_ti_parts and len(parts) == 3:
                    result["ti_parts_correct"] = True
        except Exception:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
