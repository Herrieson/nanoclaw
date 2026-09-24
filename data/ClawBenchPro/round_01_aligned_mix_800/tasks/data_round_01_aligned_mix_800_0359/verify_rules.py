import os
import json

def verify():
    state = {
        "deliverables_dir_exists": False,
        "ready_for_crm_exists": False,
        "ready_for_crm_correct_data": False,
        "volunteer_contacts_exists": False,
        "volunteer_contacts_correct_data": False,
        "used_proper_skills": False
    }

    if os.path.isdir("deliverables"):
        state["deliverables_dir_exists"] = True

    crm_path = "deliverables/ready_for_crm.json"
    if os.path.isfile(crm_path):
        state["ready_for_crm_exists"] = True
        try:
            with open(crm_path, "r", encoding="utf-8") as f:
                crm_data = json.load(f)
            
            # Expected: 
            # 01 (TechNova, LOC-E101 is East, Phone valid)
            # 07 (Eastern Telecom, LOC-E109 is East, Phone valid)
            # 04 is South but Phone has hyphens (Invalid per prompt)
            # 09 is South but Phone is 5 digits (Invalid)
            expected_companies = {"TechNova Solutions", "Eastern Telecom Partners"}
            
            if isinstance(crm_data, list):
                actual_companies = {item.get("Company_Name") for item in crm_data if isinstance(item, dict)}
                if actual_companies == expected_companies:
                    state["ready_for_crm_correct_data"] = True
        except:
            pass

    volunteer_path = "deliverables/volunteer_contacts.txt"
    if os.path.isfile(volunteer_path):
        state["volunteer_contacts_exists"] = True
        try:
            with open(volunteer_path, "r", encoding="utf-8") as f:
                content = f.read()
            # 02 (Downtown Soup Kitchen), 06 (Crescent Community Center)
            if "Downtown Soup Kitchen" in content and "Crescent Community Center" in content:
                if "TechNova" not in content:
                    state["volunteer_contacts_correct_data"] = True
        except:
            pass

    # Check if they at least tried to call skills by checking trace or logic
    # In actual evaluation, this is often done via trace analysis in verify_prompt.md
    
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
