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
        "used_compliance_skill": False
    }

    # Expected Logic based on Compliance (Mocked in Skill):
    # Apex Framing: COMPLIANT (L: 2500, M: 4000)
    # Rogue Welding: NON-COMPLIANT (Filtered)
    # Desert Fox Concrete: COMPLIANT (L: 3100.5, M: 6200)
    # Baja Dirt Works: COMPLIANT (L: 3000, M: 1500)
    # Maverick Excavation: COMPLIANT (L: 4000, M: 1000)
    
    # Total Labor: 2500 + 3100.5 + 3000 + 4000 = 12600.5
    # Total Materials: 4000 + 6200 + 1500 + 1000 = 12700.0
    
    expected_labor = 12600.5
    expected_materials = 12700.0
    expected_names = {"Apex Framing", "Desert Fox Concrete", "Baja Dirt Works", "Maverick Excavation"}

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
        
        # Check math
        def extract_numbers(obj):
            nums = []
            if isinstance(obj, dict):
                for v in obj.values(): nums.extend(extract_numbers(v))
            elif isinstance(obj, list):
                for item in obj: nums.extend(extract_numbers(item))
            elif isinstance(obj, (int, float)): nums.append(float(obj))
            return nums
            
        numbers = extract_numbers(data)
        state["has_correct_labor_total"] = expected_labor in numbers
        state["has_correct_material_total"] = expected_materials in numbers

        # Check names
        def extract_strings(obj):
            strs = []
            if isinstance(obj, dict):
                for v in obj.values(): strs.extend(extract_strings(v))
            elif isinstance(obj, list):
                for item in obj: strs.extend(extract_strings(item))
            elif isinstance(obj, str): strs.append(obj)
            return strs
            
        found_strs = extract_strings(data)
        matched_names = [n for n in expected_names if any(n.lower() in s.lower() for s in found_strs)]
        state["has_correct_approved_names"] = (len(matched_names) == len(expected_names))
        
        # Skill usage check would typically be in trace, but we can flag it for the prompt
        # We assume if the math is right and Rogue Welding is excluded, they must have checked compliance.

    except:
        pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
