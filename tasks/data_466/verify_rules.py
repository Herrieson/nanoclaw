import os
import json

def main():
    result = {
        "summary_exists": False,
        "education_correct": False,
        "environment_correct": False,
        "no_extra_categories": False,
        "script_fixed": False
    }
    
    base_dir = "."
    summary_path = os.path.join(base_dir, "summary.txt")
    script_path = os.path.join(base_dir, "process_data.py")
    
    # 1. Check if summary.txt was successfully generated
    if os.path.exists(summary_path):
        result["summary_exists"] = True
        with open(summary_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
            # 2. Check if calculations for NJ are correct
            # Education should be 120 + 45 = 165
            if "education" in content and "165" in content:
                result["education_correct"] = True
            
            # Environment should be 85 + 200 = 285
            if "environment" in content and "285" in content:
                result["environment_correct"] = True
            
            # 3. Ensure no data from NY/PA leaked in (like Healthcare which is only in NY/PA)
            if "healthcare" not in content:
                result["no_extra_categories"] = True

    # 4. Check if the script was modified (basic syntax fix check)
    if os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
            if 'item["location"] == "NJ"' in script_content:
                result["script_fixed"] = True

    # Output structural truth
    os.makedirs(".", exist_ok=True)
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    main()
