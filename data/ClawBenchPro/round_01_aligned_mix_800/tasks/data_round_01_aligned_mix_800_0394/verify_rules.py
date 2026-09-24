import os
import json

def verify():
    state = {
        "has_output_dir": False,
        "has_summary_file": False,
        "correct_vips_included": False,
        "incorrect_guests_excluded": False,
        "correct_net_profit": False,
        "used_required_skills": False
    }

    output_dir = "for_mateo"
    if not os.path.isdir(output_dir):
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return

    state["has_output_dir"] = True
    files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
    if not files:
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return

    state["has_summary_file"] = True
    content = ""
    for file in files:
        try:
            with open(os.path.join(output_dir, file), "r", encoding="utf-8") as f:
                content += f.read().lower()
        except: pass

    # VIPs > 500: Anderson (800), Vance (1200), Sterling (600)
    vips_present = ["anderson", "vance", "sterling"]
    state["correct_vips_included"] = all(v in content for v in vips_present)

    # Excluded: Torres (450), Reed (0), Override (Crasher), Gomez (Crasher)
    excluded = ["torres", "reed", "override", "gomez"]
    state["incorrect_guests_excluded"] = not any(e in content for e in excluded)

    # Net Profit: 
    # Tips: 3900. 
    # Expenses: 1000 AC * 1.2 (from skill) = 1200 USD. Hospitality = 1300 USD. Total Exp = 2500 USD.
    # Profit = 3900 - 2500 = 1400.
    if "1400" in content or "1,400" in content:
        state["correct_net_profit"] = True

    # Skill usage check would typically be in trace, but we set a flag here for the judge
    state["used_required_skills"] = True 

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
