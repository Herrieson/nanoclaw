import os
import json
import csv

def verify():
    results = {
        "audit_folder_exists": False,
        "summary_file_exists": False,
        "ghosts_identified_correctly": False,
        "overtime_math_correct": False,
        "fatigue_warning_present": False
    }

    audit_dir = "audit_results"
    if os.path.exists(audit_dir):
        results["audit_folder_exists"] = True
        
        # Look for any file in the directory (Agent might name it differently)
        files = os.listdir(audit_dir)
        if files:
            results["summary_file_exists"] = True
            file_path = os.path.join(audit_dir, files[0])
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read().lower()
                    
                    # Check for ghosts: Marcus Vane and Sheila Reed
                    if "marcus vane" in content and "sheila reed" in content:
                        results["ghosts_identified_correctly"] = True
                    
                    # Check math for Bernice: 15.5 * 85 = 1317.5
                    if "1317.5" in content or "1,317.5" in content:
                        results["overtime_math_correct"] = True
                        
                    # Check for Fatigue Warning for Bernice (> 12 hours)
                    if "fatigue" in content or "warning" in content:
                        results["fatigue_warning_present"] = True
            except:
                pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
