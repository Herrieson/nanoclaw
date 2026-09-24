import os
import json
import sys

def verify():
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "has_correct_keys": False,
        "counts_are_perfect": False,
        "no_hallucinated_doctors": True
    }

    report_path = os.path.join("secure_vault", "compliance_audit.json")
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            expected_counts = {
                "DOC-101": 3,
                "DOC-339": 1,
                "DOC-492": 2
            }
            
            # Check keys
            actual_keys = set(data.keys())
            expected_keys = set(expected_counts.keys())
            
            if actual_keys == expected_keys:
                state["has_correct_keys"] = True
            
            if actual_keys - expected_keys:
                state["no_hallucinated_doctors"] = False
                
            # Check counts
            correct_counts = True
            for doc, count in expected_counts.items():
                if data.get(doc) != count:
                    correct_counts = False
                    break
            
            if state["has_correct_keys"] and correct_counts:
                state["counts_are_perfect"] = True

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
