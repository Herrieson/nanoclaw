import os
import json
import glob

def verify():
    state = {
        "ready_for_mix_exists": False,
        "valid_stems_copied": False,
        "invalid_stems_excluded": False,
        "json_summary_correct_format": False,
        "correct_total_hours_10_75": False, # 4.75 (SE-101) + 6.0 (SE-103)
        "skill_usage_observed": False
    }

    target_dir = "ready_for_mix"
    if os.path.isdir(target_dir):
        state["ready_for_mix_exists"] = True
        
        files = set(os.listdir(target_dir))
        valid_expected = {"Vocals_Echo_Final.wav", "Drums_Echo_Raw.wav", "Bass_Neon_Main.wav", "Synth_Neon_Arp.wav"}
        invalid_forbidden = {"Guitar_Midnight_Test.wav", "Piano_Lost_Buzz.wav", "Silence_Gap.wav"}
        
        state["valid_stems_copied"] = valid_expected.issubset(files)
        state["invalid_stems_excluded"] = len(invalid_forbidden.intersection(files)) == 0

        # Check JSON formatting (Based on the "Internal Search" requirement)
        # Expected keys from Knowledge Base: "session_total_duration", "approved_assets"
        json_files = glob.glob(os.path.join(target_dir, "*.json"))
        if json_files:
            try:
                with open(json_files[0], 'r') as f:
                    data = json.load(f)
                
                # Check for strict key naming
                if "session_total_duration" in data and "approved_assets" in data:
                    state["json_summary_correct_format"] = True
                
                # Check for calculated hours: SE-101(4.75) + SE-103(6.0) = 10.75
                duration = data.get("session_total_duration")
                if duration == 10.75 or str(duration) == "10.75":
                    state["correct_total_hours_10_75"] = True
            except:
                pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
