import os
import json

def verify():
    state = {
        "has_output_dir": False,
        "has_summary_file": False,
        "correct_vips_included": False,
        "incorrect_guests_excluded": False,
        "correct_net_profit": False
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

    # Read all content within the output directory
    content = ""
    for file in files:
        file_path = os.path.join(output_dir, file)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content += f.read()
        except Exception:
            pass

    content_lower = content.lower()

    # The actual VIPs who tipped > $500
    vips_present = ["mr. anderson", "julian vance", "sophia sterling"]
    if all(vip in content_lower for vip in vips_present):
        state["correct_vips_included"] = True

    # Excluded guests: Crashers (Lucia, Crash) and VIPs <= $500 (Isabella, Marcus)
    excluded_guests = ["isabella torres", "marcus reed", "crash override", "lucia gomez"]
    if not any(guest in content_lower for guest in excluded_guests):
        state["incorrect_guests_excluded"] = True

    # Correct Net Profit Calculation:
    # Total Tips = 800 + 450 + 1200 + 600 + 0 + 100 + 750 = 3900
    # Total Expenses = 1200 + 850 + 450 = 2500
    # Net Profit = 1400
    if "1400" in content_lower or "1,400" in content_lower:
        state["correct_net_profit"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
