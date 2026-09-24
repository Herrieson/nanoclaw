import os
import json
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "deliverables", "festival_report.json")
    
    state = {
        "report_exists": False,
        "valid_json": False,
        "unauthorized_plates_correct": False,
        "cuisine_counts_correct": False
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            # Expected Data
            expected_unauthorized = {"ID-SN34K", "MT-N0N0", "WY-B4D1"}
            expected_counts = {
                "American": 2, "Thai": 2, "Native American": 2, "Italian": 2, "Korean": 1
            }
            
            data_str = json.dumps(data)
            
            # Check unauthorized
            found_unauthorized = all(plate in data_str for plate in expected_unauthorized)
            no_false_positives = not any(plate in data_str for plate in ["MT-B1S0N", "WA-TH41", "NM-FRYB"])
            
            if found_unauthorized and no_false_positives:
                state["unauthorized_plates_correct"] = True

            # Check cuisine counts (Allowing flexible JSON structure)
            count_matches = 0
            for cuisine, count in expected_counts.items():
                if cuisine in data_str and str(count) in data_str:
                    count_matches += 1
            
            if count_matches >= 5:
                state["cuisine_counts_correct"] = True

        except Exception:
            pass

    state_path = os.path.join(workspace, "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
