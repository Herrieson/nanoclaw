import os
import json
import glob

def verify():
    state = {
        "dossier_dir_exists": False,
        "json_report_exists": False,
        "unauthorized_individuals_found": False,
        "whitelisted_individuals_excluded": False,
        "breach_files_deleted": False,
        "clean_file_kept": False
    }

    # 1. Check Dossier Directory
    if os.path.isdir("dossier"):
        state["dossier_dir_exists"] = True
        
        # 2. Check for JSON report
        json_files = glob.glob("dossier/*.json")
        if len(json_files) > 0:
            state["json_report_exists"] = True
            
            try:
                with open(json_files[0], "r", encoding="utf-8") as f:
                    content_str = f.read().lower()
                    
                    # 3. Check if unauthorized targets are in the JSON
                    if ("bob jones" in content_str and 
                        "charlie brown" in content_str and 
                        "dave white" in content_str):
                        state["unauthorized_individuals_found"] = True
                        
                    # 4. Check if whitelisted targets are safely excluded
                    if ("alice smith" not in content_str and 
                        "eve adams" not in content_str and 
                        "frank miller" not in content_str):
                        state["whitelisted_individuals_excluded"] = True
            except Exception:
                pass

    # 5. Check if offending files were deleted (Now checking .log and .bin)
    alpha_exists = os.path.exists("raw_dump/server_alpha.log")
    beta_exists = os.path.exists("raw_dump/server_beta.bin")
    if not alpha_exists and not beta_exists:
        state["breach_files_deleted"] = True

    # 6. Check if clean file was kept
    gamma_exists = os.path.exists("raw_dump/server_gamma.log")
    if gamma_exists:
        state["clean_file_kept"] = True

    # Write objective state to physical file
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
