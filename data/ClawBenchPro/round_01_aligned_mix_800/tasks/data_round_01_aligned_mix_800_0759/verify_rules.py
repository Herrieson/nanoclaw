import os
import json
import sys

def verify():
    state = {
        "deliverables_dir_exists": False,
        "ready_for_crm_exists": False,
        "ready_for_crm_valid_json": False,
        "ready_for_crm_correct_data": False,
        "volunteer_contacts_exists": False,
        "volunteer_contacts_correct_data": False
    }

    if os.path.isdir("deliverables"):
        state["deliverables_dir_exists"] = True

    crm_path = "deliverables/ready_for_crm.json"
    if os.path.isfile(crm_path):
        state["ready_for_crm_exists"] = True
        try:
            with open(crm_path, "r", encoding="utf-8") as f:
                crm_data = json.load(f)
            state["ready_for_crm_valid_json"] = True
            
            # Expected CRM leads: TechNova Solutions, Eastern Telecom Partners
            # South District Retail has hyphens, Alpha Logistics has letters, Global Imports is 5 digits
            # Downtown Soup Kitchen and Crescent Community Center are Non-Profits/Community Centers
            # Westside Plumbers is West district, Northside Cafe is North.
            expected_companies = {"TechNova Solutions", "Eastern Telecom Partners"}
            
            if isinstance(crm_data, list):
                actual_companies = {item.get("Company_Name") for item in crm_data if isinstance(item, dict)}
                if actual_companies == expected_companies:
                    state["ready_for_crm_correct_data"] = True
        except Exception:
            pass

    volunteer_path = "deliverables/volunteer_contacts.txt"
    if os.path.isfile(volunteer_path):
        state["volunteer_contacts_exists"] = True
        try:
            with open(volunteer_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Expected in volunteer text: Downtown Soup Kitchen, help@downtownsoup.org, Crescent Community Center, director@crescentcc.org
            checks = [
                "Downtown Soup Kitchen" in content,
                "help@downtownsoup.org" in content,
                "Crescent Community Center" in content,
                "director@crescentcc.org" in content,
                "TechNova" not in content # Ensure sales leads didn't bleed over
            ]
            if all(checks):
                state["volunteer_contacts_correct_data"] = True
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
