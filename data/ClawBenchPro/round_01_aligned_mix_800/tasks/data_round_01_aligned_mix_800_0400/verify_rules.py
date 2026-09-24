import os
import json
import sys

def verify():
    workdir = sys.argv[1] if len(sys.argv) > 1 else "."
    briefing_dir = os.path.join(workdir, "briefing")
    
    state = {
        "briefing_file_exists": False,
        "has_fake_00": False,
        "has_bad_888": False,
        "no_false_positives": True,
        "used_ocr_skill": False,
        "used_api_skill": False
    }

    # Check for briefing report
    if os.path.exists(briefing_dir) and os.path.isdir(briefing_dir):
        files = [f for f in os.listdir(briefing_dir) if os.path.isfile(os.path.join(briefing_dir, f))]
        if len(files) > 0:
            state["briefing_file_exists"] = True
            content = ""
            for file_name in files:
                with open(os.path.join(briefing_dir, file_name), "r", encoding="utf-8") as f:
                    content += f.read()

            # Targets
            if "CA-9FAKE00" in content:
                state["has_fake_00"] = True
            if "CA-BAD888" in content:
                state["has_bad_888"] = True

            # Valid ones should NOT be in the poacher list
            valid_plates = ["CA-5GTR222", "CA-1ABC123", "CA-8HJK999"]
            for valid in valid_plates:
                if valid in content:
                    state["no_false_positives"] = False

    # Check skill usage from a hidden log the skills create
    log_path = os.path.join(workdir, "logs/skill_usage.jsonl")
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            logs = f.read()
            if "ocr_license_extractor" in logs:
                state["used_ocr_skill"] = True
            if "state_dmv_query_api" in logs:
                state["used_api_skill"] = True

    state_file_path = os.path.join(workdir, "state.json")
    with open(state_file_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
