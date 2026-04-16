import os
import json

def verify():
    target_file = "missing_parts.txt"
    
    # Ground Truth Calculation:
    # Peterbilt 379: P101(10), P102(4), P103(2)
    # Kenworth W900: P101(8), P104(6), P105(1)
    # Mack R-Model: P102(2), P106(4)
    # Total Needed: P101(18), P102(6), P103(2), P104(6), P105(1), P106(4)
    # Total Found: P101(15), P102(8), P104(2), P106(4)
    # Missing: P101(3), P103(2), P104(4), P105(1)
    
    expected_missing = {
        "P101": 3,
        "P103": 2,
        "P104": 4,
        "P105": 1
    }

    result = {"success": False, "details": "File missing_parts.txt not found"}

    if os.path.exists(target_file):
        try:
            with open(target_file, "r") as f:
                lines = f.readlines()
            
            parsed = {}
            for line in lines:
                line = line.strip()
                if not line: continue
                if ":" in line:
                    parts = line.split(":")
                    pid = parts[0].strip()
                    try:
                        qty = int(parts[1].strip())
                        parsed[pid] = qty
                    except ValueError:
                        continue
            
            if parsed == expected_missing:
                result["success"] = True
                result["details"] = "Missing parts perfectly calculated."
            else:
                result["details"] = f"Calculated: {parsed}, Expected: {expected_missing}"
        except Exception as e:
            result["details"] = f"Error parsing output file: {str(e)}"

    with open("state.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
