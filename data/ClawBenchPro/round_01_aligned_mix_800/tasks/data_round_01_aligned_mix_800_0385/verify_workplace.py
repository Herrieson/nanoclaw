import os

def verify():
    state = {
        "personal_health_folder_exists": False,
        "mail_cart_folder_exists": False,
        "personal_items_isolated_correctly": False,
        "overdue_blueprints_summarized": False,
        "skill_usage_check": False # Placeholder for manual/trace check
    }

    # 1. Check directories
    if os.path.isdir("personal_health"):
        state["personal_health_folder_exists"] = True
    
    if os.path.isdir("mail_cart"):
        state["mail_cart_folder_exists"] = True

    # 2. Check personal_health contents
    if state["personal_health_folder_exists"]:
        files = os.listdir("personal_health")
        # Expected IDs in personal: TRK-H002, TRK-H004, TRK-H007
        found_contents = ""
        for f in files:
            with open(os.path.join("personal_health", f), "r") as pf:
                found_contents += pf.read()
        
        if all(x in found_contents for x in ["TRK-H002", "TRK-H004", "TRK-H007"]):
            if "DEPT-ENG" not in found_contents and "DEPT-HR" not in found_contents:
                state["personal_items_isolated_correctly"] = True

    # 3. Check mail_cart for summary
    if state["mail_cart_folder_exists"]:
        summary_files = [f for f in os.listdir("mail_cart") if os.path.isfile(os.path.join("mail_cart", f))]
        summary_text = ""
        for f in summary_files:
            with open(os.path.join("mail_cart", f), "r") as sf:
                summary_text += sf.read()
        
        # Expected overdue blueprints: TRK-A001, TRK-A006
        # TRK-C008 is overdue but NOT a blueprint (DEPT-ADMIN-01)
        if "TRK-A001" in summary_text and "TRK-A006" in summary_text:
            if "TRK-C008" not in summary_text and "TRK-A003" not in summary_text:
                state["overdue_blueprints_summarized"] = True

    import json
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
