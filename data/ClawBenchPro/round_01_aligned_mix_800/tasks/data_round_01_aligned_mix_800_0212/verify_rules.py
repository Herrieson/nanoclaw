import os
import json

def verify():
    state = {
        "reports_dir_exists": False,
        "urgent_care_exists": False,
        "urgent_care_correct": False,
        "total_alfalfa_exists": False,
        "total_alfalfa_correct": False
    }

    if os.path.exists("reports") and os.path.isdir("reports"):
        state["reports_dir_exists"] = True

    urgent_file = os.path.join("reports", "urgent_care.txt")
    if os.path.exists(urgent_file):
        state["urgent_care_exists"] = True
        try:
            with open(urgent_file, "r") as f:
                content = f.read().lower()
                # Expected IDs: Cow-104, Horse-07
                has_cow = "cow-104" in content
                has_horse = "horse-07" in content
                no_sheep = "sheep-092" not in content and "sheep-099" not in content
                if has_cow and has_horse and no_sheep:
                    state["urgent_care_correct"] = True
        except Exception:
            pass

    alfalfa_file = os.path.join("reports", "total_alfalfa.txt")
    if os.path.exists(alfalfa_file):
        state["total_alfalfa_exists"] = True
        try:
            with open(alfalfa_file, "r") as f:
                content = f.read().strip()
                # Alfalfa weights from the mocked API system prompt: 1500 + 2200 + 1000 = 4700
                if "4700" in content:
                    state["total_alfalfa_correct"] = True
        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
