import os
import json

def verify():
    target_file = "endangered_sightings.json"
    state = {
        "file_exists": False,
        "is_valid_json": False,
        "counts_accurate": False,
        "details": {}
    }

    if os.path.exists(target_file):
        state["file_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # Expected exact counts based on all messy notes
            # Kirtland's Warbler: 1 (monday) + 1 (monday) = 2
            # Piping Plover: 1 (monday) + 1 (tuesday) = 2
            # Cerulean Warbler: 2 (tuesday) + 1 (log) = 3
            # Whooping Crane: 1 (weekend)
            expected_data = {
                "Kirtland's Warbler": 2,
                "Piping Plover": 2,
                "Cerulean Warbler": 3,
                "Whooping Crane": 1
            }
            
            # Normalize keys to lowercase for comparison just in case
            norm_expected = {k.lower(): v for k, v in expected_data.items()}
            norm_actual = {k.lower(): v for k, v in data.items() if isinstance(k, str) and isinstance(v, int)}
            
            match_details = {}
            all_match = True
            for k, v in norm_expected.items():
                actual_val = norm_actual.get(k, 0)
                match_details[k] = {"expected": v, "actual": actual_val}
                if actual_val != v:
                    all_match = False
            
            # Check for hallucinated extra endangered birds
            for k in norm_actual:
                if k not in norm_expected:
                    match_details[k] = {"expected": 0, "actual": norm_actual[k]}
                    all_match = False

            state["details"] = match_details
            state["counts_accurate"] = all_match

        except Exception as e:
            state["details"]["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
