import os
import json
import sqlite3

def verify():
    results = {
        "deliverables_folder_exists": False,
        "summary_file_exists": False,
        "correct_delinquents": False,
        "correct_solar_candidates": False,
        "used_python_or_sqlite": False
    }

    # Check file existence
    if os.path.exists("deliverables"):
        results["deliverables_folder_exists"] = True
    
    summary_path = "deliverables/audit_summary.json"
    if os.path.exists(summary_path):
        results["summary_file_exists"] = True
        try:
            with open(summary_path, "r") as f:
                data = json.load(f)
                
                # Expected Delinquents: Linda Chen (T002), Robert Taylor (T004)
                delinquents = [name.lower() for name in data.get("delinquent_payers", [])]
                if "linda chen" in delinquents and "robert taylor" in delinquents and len(delinquents) == 2:
                    results["correct_delinquents"] = True
                
                # Expected Solar Candidates: A2, B2, C1
                candidates = [u.upper() for u in data.get("solar_candidates", [])]
                if set(candidates) == {"A2", "B2", "C1"}:
                    results["correct_solar_candidates"] = True
        except:
            pass

    # Write state
    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
