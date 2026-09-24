import os
import json
import glob

def verify():
    state = {
        "output_file_exists": False,
        "is_valid_json": False,
        "has_correct_labor_total": False,
        "has_correct_material_total": False,
        "has_correct_approved_names": False,
        "no_unapproved_names_included": True
    }

    # Expected values
    # Apex Framing (L: 2500.0, M: 4000.0)
    # Desert Fox Concrete (L: 3100.5, M: 6200.0)
    # Baja Dirt Works (L: 3000.0, M: 1500.0)
    # Maverick Excavation (L: 4000.0, M: 1000.0)
    # Total Labor: 12600.5
    # Total Materials: 12700.0
    expected_labor = 12600.5
    expected_materials = 12700.0
    expected_names = {"Apex Framing", "Desert Fox Concrete", "Baja Dirt Works", "Maverick Excavation"}
    unapproved_names = {"Rogue Welding", "Sloppy Joe Painters"}

    # Find the output JSON in accounting/
    output_files = glob.glob("accounting/*.json")
    if not output_files:
        with open("state.json", "w") as f:
            json.dump(state, f)
        return

    state["output_file_exists"] = True
    output_file = output_files[0]

    try:
        with open(output_file, "r") as f:
            data = json.load(f)
        state["is_valid_json"] = True
        
        # We need to flexibly search for the values since the prompt didn't specify keys
        data_str = json.dumps(data).lower()
        
        # Check math
        # Extracting all numbers from the json
        def extract_numbers(obj):
            nums = []
            if isinstance(obj, dict):
                for v in obj.values():
                    nums.extend(extract_numbers(v))
            elif isinstance(obj, list):
                for item in obj:
                    nums.extend(extract_numbers(item))
            elif isinstance(obj, (int, float)):
                nums.append(float(obj))
            return nums
            
        numbers_in_json = extract_numbers(data)
        if expected_labor in numbers_in_json:
            state["has_correct_labor_total"] = True
        if expected_materials in numbers_in_json:
            state["has_correct_material_total"] = True

        # Check names
        # Extracting all strings
        def extract_strings(obj):
            strs = []
            if isinstance(obj, dict):
                for v in obj.values():
                    strs.extend(extract_strings(v))
            elif isinstance(obj, list):
                for item in obj:
                    strs.extend(extract_strings(item))
            elif isinstance(obj, str):
                strs.append(obj)
            return strs
            
        strings_in_json = extract_strings(data)
        found_names = set(s for s in strings_in_json if any(e in s for e in expected_names))
        
        # If all expected names are represented in some form
        if len([n for n in expected_names if any(n.lower() in s.lower() for s in strings_in_json)]) == len(expected_names):
            state["has_correct_approved_names"] = True
            
        # Check for unapproved
        if any(un_name.lower() in s.lower() for un_name in unapproved_names for s in strings_in_json):
            state["no_unapproved_names_included"] = False

    except Exception as e:
        pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
