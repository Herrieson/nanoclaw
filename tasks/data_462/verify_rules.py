import os
import json
import re

def verify():
    workspace = "."
    state = {
        "files_found": [],
        "missing_files": [],
        "content_checks": {}
    }

    # Expected top 3 units based on env_builder logic
    expected_units = ["203", "301", "102"]
    expected_names = {
        "203": "Frank Castle",
        "301": "Grace Hopper",
        "102": "Bob Johnson"
    }

    for unit in expected_units:
        filename = f"notice_{unit}.txt"
        filepath = os.path.join(workspace, filename)
        if os.path.exists(filepath):
            state["files_found"].append(filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().lower()
                
                # Check 1: Tenant Name
                has_name = expected_names[unit].lower() in content
                
                # Check 2: The exact phrase
                has_phrase = "mandatory water and energy conservation" in content
                
                # Check 3: A number indicating total cost (just check if numbers > 3000 are present)
                # We expect totals around 3800-4800
                numbers = re.findall(r'\d{4,}', content)
                has_cost = any(3000 < int(num) < 6000 for num in numbers) or any(3000 < float(n.replace(',', '')) < 6000 for n in re.findall(r'\d{1,},\d{3}(?:\.\d{2})?', content))

                state["content_checks"][unit] = {
                    "has_correct_name": has_name,
                    "has_mandatory_phrase": has_phrase,
                    "has_reasonable_cost_number": has_cost
                }
        else:
            state["missing_files"].append(filename)

    # Check if they created files for the WRONG units
    all_txts = [f for f in os.listdir(workspace) if f.startswith("notice_") and f.endswith(".txt")]
    unexpected_files = [f for f in all_txts if f not in [f"notice_{u}.txt" for u in expected_units]]
    state["unexpected_files"] = unexpected_files

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
