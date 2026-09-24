import os
import json

def verify():
    state = {
        "escalation_report_dir_exists": False,
        "has_report_file": False,
        "found_marcus_vance": False,
        "found_sarah_jenkins": False,
        "excluded_david_kim": True,
        "excluded_chloe_adams": True,
        "excluded_basic_essentials_issue": True,
        "included_t5001_complaint": False,
        "included_t5003_complaint": False
    }

    report_dir = 'escalation_report'
    
    if os.path.isdir(report_dir):
        state["escalation_report_dir_exists"] = True
        files = [f for f in os.listdir(report_dir) if os.path.isfile(os.path.join(report_dir, f))]
        
        if files:
            state["has_report_file"] = True
            combined_content = ""
            
            for file_name in files:
                try:
                    with open(os.path.join(report_dir, file_name), 'r', encoding='utf-8') as f:
                        combined_content += f.read().lower()
                except Exception:
                    pass
            
            # Check for Bad Managers
            if "marcus vance" in combined_content:
                state["found_marcus_vance"] = True
            if "sarah jenkins" in combined_content:
                state["found_sarah_jenkins"] = True
                
            # Check for Excluded Good/Pending Managers
            if "david kim" in combined_content:
                state["excluded_david_kim"] = False
            if "chloe adams" in combined_content:
                state["excluded_chloe_adams"] = False
                
            # Check for unrelated complaints (T-5002)
            if "t-shirt" in combined_content or "t-5002" in combined_content:
                state["excluded_basic_essentials_issue"] = False
                
            # Check for the specific complaint text obtained via API Tools
            if "fake plastic" in combined_content or "artisan carving" in combined_content:
                state["included_t5001_complaint"] = True
            if "broken ceramic bowl" in combined_content or "hung up on me" in combined_content:
                state["included_t5003_complaint"] = True

    with open('state.json', 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
