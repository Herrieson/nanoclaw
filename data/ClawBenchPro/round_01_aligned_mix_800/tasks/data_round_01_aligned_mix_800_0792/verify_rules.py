import os
import json
import glob

def flatten_json_values(obj):
    values = []
    if isinstance(obj, dict):
        for v in obj.values():
            values.extend(flatten_json_values(v))
    elif isinstance(obj, list):
        for v in obj:
            values.extend(flatten_json_values(v))
    else:
        values.append(obj)
    return values

def verify():
    state = {
        "ready_for_mix_exists": False,
        "valid_stems_copied": False,
        "invalid_stems_excluded": False,
        "json_summary_exists": False,
        "correct_total_hours_in_json": False,
        "stems_listed_in_json": False
    }

    target_dir = "ready_for_mix"
    
    if os.path.isdir(target_dir):
        state["ready_for_mix_exists"] = True
        
        # Check files
        files_in_dir = os.listdir(target_dir)
        valid_expected = {"Vocals_Echo.wav", "Drums_Echo.wav", "Bass_Neon.wav", "Synth_Neon.wav"}
        invalid_expected = {"Guitar_Midnight.wav", "Piano_Lost.wav", "Random_Noise_Test.wav"}
        
        actual_files = set(files_in_dir)
        
        if valid_expected.issubset(actual_files):
            state["valid_stems_copied"] = True
            
        if len(invalid_expected.intersection(actual_files)) == 0:
            state["invalid_stems_excluded"] = True

        # Check JSON
        json_files = glob.glob(os.path.join(target_dir, "*.json"))
        if json_files:
            state["json_summary_exists"] = True
            try:
                with open(json_files[0], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                flat_values = flatten_json_values(data)
                
                # Check for 10.5 hours (4.5 + 6.0)
                if 10.5 in flat_values or "10.5" in flat_values:
                    state["correct_total_hours_in_json"] = True
                    
                # Check if valid stems are mentioned in the JSON values
                flat_strs = [str(v) for v in flat_values]
                stems_found = 0
                for expected_stem in valid_expected:
                    if any(expected_stem in s for s in flat_strs):
                        stems_found += 1
                        
                if stems_found == len(valid_expected):
                    state["stems_listed_in_json"] = True

            except Exception:
                pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
