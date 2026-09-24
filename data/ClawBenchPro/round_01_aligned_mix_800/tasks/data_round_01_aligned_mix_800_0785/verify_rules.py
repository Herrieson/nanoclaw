import os
import json

def verify():
    state = {
        "personal_health_folder_exists": False,
        "mail_cart_folder_exists": False,
        "personal_items_isolated_correctly": False,
        "no_company_items_in_personal": False,
        "overdue_blueprints_summarized": False,
        "non_blueprints_excluded": False
    }

    # 1. Check directories
    if os.path.isdir("personal_health"):
        state["personal_health_folder_exists"] = True
    
    if os.path.isdir("mail_cart"):
        state["mail_cart_folder_exists"] = True

    # 2. Check personal_health contents
    if state["personal_health_folder_exists"]:
        files = os.listdir("personal_health")
        personal_ids_found = set()
        company_ids_found = set()
        
        for file in files:
            if file.endswith(".json"):
                try:
                    with open(os.path.join("personal_health", file), "r") as f:
                        data = json.load(f)
                        if "Mailroom - Personal" in data.get("recipient", ""):
                            personal_ids_found.add(data.get("id"))
                        else:
                            company_ids_found.add(data.get("id"))
                except:
                    pass
        
        # Expected personal IDs: TRK-H002, TRK-H004, TRK-H007
        expected_personal = {"TRK-H002", "TRK-H004", "TRK-H007"}
        if expected_personal.issubset(personal_ids_found):
            state["personal_items_isolated_correctly"] = True
            
        if len(company_ids_found) == 0 and len(files) > 0:
            state["no_company_items_in_personal"] = True

    # 3. Check mail_cart contents for summary
    if state["mail_cart_folder_exists"]:
        files = os.listdir("mail_cart")
        summary_text = ""
        for file in files:
            try:
                with open(os.path.join("mail_cart", file), "r") as f:
                    summary_text += f.read() + "\n"
            except:
                pass
        
        # Expected overdue blueprints: TRK-A001, TRK-A006
        if "TRK-A001" in summary_text and "TRK-A006" in summary_text:
            state["overdue_blueprints_summarized"] = True
            
        # Expected NOT to include TRK-C008 (overdue but not blueprints) or TRK-A003 (blueprint but on time)
        if "TRK-C008" not in summary_text and "TRK-A003" not in summary_text:
            state["non_blueprints_excluded"] = True

    # Dump state to physical file
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
