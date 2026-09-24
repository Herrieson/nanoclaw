import os
import json

def verify():
    state = {
        "summary_exists": False,
        "valid_json": False,
        "total_value_correct": False,
        "cases_correct": False
    }

    target_file = os.path.join("precinct_desk", "bolo_summary.json")
    
    if os.path.exists(target_file):
        state["summary_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            state["valid_json"] = True

            # Logic:
            # 101: Rolex -> 500
            # 102: Ford F-150 -> 25000 (Neck Tattoo)
            # 104: MacBook Pro -> 1200 (Neck Tattoo)
            # 105: Designer Wallet -> 300
            # Total: 27000
            # Cases: 102, 104
            
            val = data.get("total_stolen_value")
            cases = data.get("neck_tattoo_cases")

            if str(val) == "27000" or val == 27000:
                state["total_value_correct"] = True
            
            if isinstance(cases, list):
                str_cases = sorted([str(c).replace("audio_case_", "").replace(".wav.log", "").replace("10", "10") for c in cases])
                # Normalize case IDs: some agents might use 102 or audio_case_102
                normalized = []
                for c in str_cases:
                    if "102" in c: normalized.append("102")
                    if "104" in c: normalized.append("104")
                if sorted(list(set(normalized))) == ["102", "104"]:
                    state["cases_correct"] = True
            
        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
