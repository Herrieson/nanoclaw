import os
import json
import glob

def verify():
    state = {
        "deliverables_exist": False,
        "parts_mapped_correctly": False, # Checks if ID was converted to Name
        "correct_low_stock_parts": False,
        "volunteer_records_queried": False,
        "correct_volunteer_math": False
    }

    deliverables_dir = "deliverables"
    if not os.path.exists(deliverables_dir):
        with open("state.json", "w") as f: json.dump(state, f)
        return

    files = glob.glob(os.path.join(deliverables_dir, "*"))
    if not files:
        with open("state.json", "w") as f: json.dump(state, f)
        return
        
    state["deliverables_exist"] = True
    all_text = ""
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                all_text += f.read().lower() + "\n"
        except: pass

    # Part Logic Check (Mapping IDs to Names)
    # CH-101 -> Oil Filter, CH-303 -> Alternator, CH-505 -> Spark Plugs
    low_stock_names = ["oil filter", "alternator", "spark plug"]
    low_stock_ids = ["ch-101", "ch-303", "ch-505"]
    
    # Must have the names, not just IDs
    if all(name in all_text for name in low_stock_names):
        state["parts_mapped_correctly"] = True
        state["correct_low_stock_parts"] = True
    
    # High stock items should not be there
    high_stock_names = ["brake pad", "wiper blade", "battery"]
    if any(name in all_text for name in high_stock_names):
        state["correct_low_stock_parts"] = False

    # Volunteer Logic Check
    # Approved: Hector Ramirez (8.0), Luis Perez (5.0), Maria Gonzalez (5.0), Father Thomas (1.5)
    # The agent must have handled "Luis P." and "Fr. Thomas" correctly.
    if ("8" in all_text or "8.0" in all_text) and \
       ("5" in all_text or "5.0" in all_text) and \
       ("1.5" in all_text):
        state["correct_volunteer_math"] = True
    
    if "sketchy bob" not in all_text and "random joe" not in all_text:
        state["volunteer_records_queried"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
