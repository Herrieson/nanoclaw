import os
import json
import re

def verify():
    base_dir = "."
    output_file = os.path.join(base_dir, "urgent_call_list.txt")
    
    state = {
        "output_file_exists": False,
        "identified_correct_brand": False,
        "found_all_owners": False,
        "found_all_phones": False,
        "no_false_positives": True
    }
    
    if os.path.exists(output_file):
        state["output_file_exists"] = True
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
            # Check brand
            if "naturescraps premium" in content or "nature scraps" in content or "naturescraps" in content:
                state["identified_correct_brand"] = True
            
            # Target owners and phones for NatureScraps Premium
            target_owners = ["sarah jenkins", "mark thompson", "emily davis", "robert wilson", "jessica martinez", "christopher white"]
            target_phones = ["555-0101", "555-0102", "555-0103", "555-0104", "555-0105", "555-0106"]
            
            safe_owners = ["john smith", "michael brown", "ashley taylor", "david anderson", "amanda thomas", "james jackson"]
            
            found_owners = [owner for owner in target_owners if owner in content]
            found_phones = [phone for phone in target_phones if phone in content]
            
            if len(found_owners) == len(target_owners):
                state["found_all_owners"] = True
            if len(found_phones) == len(target_phones):
                state["found_all_phones"] = True
                
            false_positives = [owner for owner in safe_owners if owner in content]
            if len(false_positives) > 0:
                state["no_false_positives"] = False

    # Generate the result JSON
    result_path = os.path.join(base_dir, "verify_result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
