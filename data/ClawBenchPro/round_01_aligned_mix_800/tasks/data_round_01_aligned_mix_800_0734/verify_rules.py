import os
import json
import glob

def verify():
    results = {
        "deliverables_folder_exists": os.path.isdir("deliverables"),
        "report_exists": False,
        "unauthorized_detected_correctly": False,
        "math_is_accurate": False,
        "format_is_structured": False
    }

    # Find any json or markdown file in deliverables
    files = glob.glob("deliverables/*")
    if files:
        results["report_exists"] = True
        
        # Check content (assuming Agent creates a JSON or clear text)
        content = ""
        report_path = files[0]
        try:
            with open(report_path, "r") as f:
                content = f.read().lower()
            
            # Check for unauthorized names
            if "unknown stranger" in content and "intruder ivan" in content:
                results["unauthorized_detected_correctly"] = True
            
            # Check math: 
            # Alice: 4 + 2 = 6
            # Bob: 3 + 2 = 5 (ignoring "invalid_data")
            # Charlie: 2.5
            # Diana: 6
            if "alice smith" in content and ("6" in content or "6.0" in content):
                if "bob johnson" in content and ("5" in content or "5.0" in content):
                    results["math_is_accurate"] = True
            
            # Check if structured (looks like JSON or a table)
            if "{" in content or "|" in content or "\t" in content:
                results["format_is_structured"] = True
        except:
            pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
