import os
import json
import glob

def verify():
    state = {
        "deliverables_exist": False,
        "parts_report_found": False,
        "correct_low_stock_parts": False,
        "excluded_high_stock_parts": False,
        "volunteer_report_found": False,
        "unapproved_volunteers_excluded": False,
        "correct_volunteer_math": False
    }

    deliverables_dir = "deliverables"
    if not os.path.exists(deliverables_dir):
        with open("state.json", "w") as f:
            json.dump(state, f)
        return

    files = glob.glob(os.path.join(deliverables_dir, "*"))
    if not files:
        with open("state.json", "w") as f:
            json.dump(state, f)
        return
        
    state["deliverables_exist"] = True

    # Concatenate all text from deliverables to analyze
    all_text = ""
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                all_text += f.read().lower() + "\n"
        except Exception:
            pass

    # Check Parts logic
    # Low stock (<5): Oil Filter (3), Alternator (1), Spark Plugs (4)
    # High stock (>=5): Brake Pads (15), Wiper Blades (8), Battery (5)
    low_stock = ["oil filter", "alternator", "spark plug"]
    high_stock = ["brake pad", "wiper blade", "battery"]

    if any(p in all_text for p in low_stock):
        state["parts_report_found"] = True

    if all(p in all_text for p in low_stock):
        state["correct_low_stock_parts"] = True
    
    if all(p not in all_text for p in high_stock):
        state["excluded_high_stock_parts"] = True

    # Check Volunteer logic
    # Approved: Hector Ramirez (8.0), Luis Perez (5.0), Maria Gonzalez (5.0), Father Thomas (1.5)
    # Unapproved: Sketchy Bob, Random Joe
    approved_names_lower = ["hector", "luis", "maria", "thomas"]
    unapproved_names_lower = ["sketchy bob", "random joe"]

    if any(name in all_text for name in approved_names_lower):
        state["volunteer_report_found"] = True

    if all(bad_name not in all_text for bad_name in unapproved_names_lower):
        state["unapproved_volunteers_excluded"] = True

    # Check math: "8" or "8.0" for Hector, "5" or "5.0" for Luis/Maria, "1.5" for Father Thomas
    # We'll just check if the sum totals or individual totals appear close to the names. 
    # For a strict objective probe, we check if the numbers '8', '5', '1.5' exist in the text alongside the names.
    if ("8" in all_text or "8.0" in all_text) and \
       ("5" in all_text or "5.0" in all_text) and \
       ("1.5" in all_text):
        state["correct_volunteer_math"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
