import os
import json

def verify():
    state = {
        "report_file_exists": False,
        "is_valid_json": False,
        "has_correct_total_cost": False,
        "has_mary_johnson": False,
        "has_alice_vance": False,
        "no_false_positives": True
    }

    report_path = "overdue_antiques_report.json"
    
    if os.path.exists(report_path):
        state["report_file_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # Convert JSON to a raw string to easily search for required data
            # since the prompt didn't specify an exact schema
            raw_content = json.dumps(data).lower()
            
            # The overdue restricted books are B-101 ($850) and B-103 ($1200)
            # Total replacement cost should be exactly 2050
            if "2050" in raw_content or "2050.0" in raw_content or "2050.00" in raw_content:
                state["has_correct_total_cost"] = True
                
            if "mary johnson" in raw_content:
                state["has_mary_johnson"] = True
                
            if "alice vance" in raw_content:
                state["has_alice_vance"] = True
                
            # Bobby Tables had a restricted book (B-102) but it's due 2023-10-15 (NOT overdue before Oct 1st)
            # Timmy Smith and Sarah had non-restricted books
            if "bobby tables" in raw_content or "timmy smith" in raw_content or "sarah" in raw_content:
                state["no_false_positives"] = False

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
