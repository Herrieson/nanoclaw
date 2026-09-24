import os
import json

def verify():
    # Initialize the objective state dictionary
    state = {
        "deliverables_folder_exists": False,
        "shortlist_file_exists": False,
        "top_3_correctly_identified": False,
        "blacklisted_influencer_excluded": True,
        "dirty_data_excluded": True
    }

    deliverables_path = "deliverables"

    # 1. Check if the deliverables folder exists
    if os.path.exists(deliverables_path) and os.path.isdir(deliverables_path):
        state["deliverables_folder_exists"] = True
        
        # 2. Check if there is any file inside deliverables
        files = os.listdir(deliverables_path)
        if files:
            state["shortlist_file_exists"] = True
            
            # Read all text-based files in the deliverables folder to check contents
            combined_content = ""
            for file_name in files:
                file_path = os.path.join(deliverables_path, file_name)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            combined_content += f.read()
                    except Exception:
                        pass
            
            # 3. Verify the presence of the correct Top 3 influencers
            # Based on the math: Derma_Diana (2500), Chemistry_Chloe (2100), Aria_Style (1350)
            has_diana = "Derma_Diana" in combined_content
            has_chloe = "Chemistry_Chloe" in combined_content
            has_aria = "Aria_Style" in combined_content
            
            if has_diana and has_chloe and has_aria:
                state["top_3_correctly_identified"] = True
                
            # 4. Verify that the blacklisted influencer (BioTech_Bob) is NOT recommended
            if "BioTech_Bob" in combined_content:
                state["blacklisted_influencer_excluded"] = False
                
            # 5. Verify that the malformed data row was ignored
            if "Fake_User" in combined_content:
                state["dirty_data_excluded"] = False

    # Dump the objective reality to state.json
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
