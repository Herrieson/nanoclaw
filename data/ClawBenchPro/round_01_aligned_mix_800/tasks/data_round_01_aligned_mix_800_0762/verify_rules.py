import os
import json

def verify():
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "grade_4_hours_correct": False,
        "grade_5_hours_correct": False,
        "grade_6_hours_correct": False,
        "missing_slips_correct": False
    }
    
    report_path = 'final_docs/report.json'
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # Helper to find if a target value exists anywhere in the JSON values
            def find_value(obj, targets):
                if isinstance(obj, dict):
                    for v in obj.values():
                        if v in targets: return True
                        if find_value(v, targets): return True
                elif isinstance(obj, list):
                    for item in obj:
                        if item in targets: return True
                        if find_value(item, targets): return True
                return False
                
            # Grade 4 total: 2 + 4 + 3 = 9
            if find_value(data, [9, "9"]): state["grade_4_hours_correct"] = True
            # Grade 5 total: 4 + 3 + 1 = 8
            if find_value(data, [8, "8"]): state["grade_5_hours_correct"] = True
            # Grade 6 total: 5 + 2 = 7
            if find_value(data, [7, "7"]): state["grade_6_hours_correct"] = True
            
            # Extract all string values to check for missing slips names
            names = []
            def extract_strings(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        names.append(str(k).lower())
                        extract_strings(v)
                elif isinstance(obj, list):
                    for item in obj:
                        extract_strings(item)
                elif isinstance(obj, str):
                    names.append(obj.lower())
                    
            extract_strings(data)
            
            # The students without a 'Signed' status who showed up are Leo, Sam, Alex
            if 'leo' in names and 'sam' in names and 'alex' in names:
                # Ensure they didn't just dump all students (Mia and Zoe had signed slips)
                if 'mia' not in names and 'zoe' not in names:
                    state["missing_slips_correct"] = True
                    
        except Exception:
            pass

    with open('state.json', 'w') as f:
        json.dump(state, f)

if __name__ == '__main__':
    verify()
