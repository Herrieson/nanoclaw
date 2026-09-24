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
            
            # Check unauthorized plates
            expected_unauthorized = {"ID-SN34K", "MT-N0N0", "WY-B4D1"}
            
            # The agent might nest things, so we search the JSON values
            data_str = json.dumps(data)
            found_unauthorized = all(plate in data_str for plate in expected_unauthorized)
            no_false_positives = not any(plate in data_str for plate in ["MT-B1S0N", "WA-TH41", "NM-FRYB", "NY-PZZA"])
            
            if found_unauthorized and no_false_positives:
                state["unauthorized_plates_correct"] = True

            # Check cuisine counts
            expected_counts = {
                "American": 2,
                "Thai": 2,
                "Native American": 2,
                "Italian": 2,
                "Korean": 1
            }
            
            counts_correct = True
            for cuisine, expected_count in expected_counts.items():
                if cuisine not in data_str or str(expected_count) not in data_str:
                    counts_correct = False
            
            # Simple heuristic since schemas vary: check if the counts mapping seems roughly present
            # We'll do a slightly deeper dict check if possible
            def find_counts(obj):
                if isinstance(obj, dict):
                    # If this dict looks like our counts
                    if "American" in obj and obj["American"] == 2:
                        return obj
                    for v in obj.values():
                        res = find_counts(v)
                        if res: return res
                return None
            
            counts_obj = find_counts(data)
            if counts_obj:
                match = True
                for c, v in expected_counts.items():
                    if counts_obj.get(c) != v:
                        match = False
                if match:
                    state["cuisine_counts_correct"] = True
            elif counts_correct:
                # Fallback to string matching heuristic if deeply nested or differently formatted
                state["cuisine_counts_correct"] = True

        except Exception:
            pass

    state_path = os.path.join(workspace, "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
