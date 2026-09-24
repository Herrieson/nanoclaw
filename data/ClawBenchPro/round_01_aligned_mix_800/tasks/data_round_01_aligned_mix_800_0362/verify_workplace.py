import os
import json

def verify():
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "grade_4_hours_correct": False,
        "grade_5_hours_correct": False,
        "grade_6_hours_correct": False,
        "missing_slips_correct": False,
        "student_ids_present": False
    }
    
    report_path = 'final_docs/report.json'
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # Target hours calculation:
            # Morning: Leo(5,4), Mia(6,5), Zoe(5,3), Carlos(4,2)
            # Afternoon: Sam(6,2), Alex(4,4), Chloe(5,1), Emma(4,3)
            # Grade 4 total: Carlos(2) + Alex(4) + Emma(3) = 9
            # Grade 5 total: Leo(4) + Zoe(3) + Chloe(1) = 8
            # Grade 6 total: Mia(5) + Sam(2) = 7
            
            def find_val(d, target):
                s = str(d)
                return str(target) in s

            if find_val(data, 9): state["grade_4_hours_correct"] = True
            if find_val(data, 8): state["grade_5_hours_correct"] = True
            if find_val(data, 7): state["grade_6_hours_correct"] = True
            
            # Check for IDs (Skill returns IDs like SID-XXXX)
            if "SID-" in str(data):
                state["student_ids_present"] = True

            # Missing slips: Leo, Sam, Alex
            content_str = str(data).lower()
            if 'leo' in content_str and 'sam' in content_str and 'alex' in content_str:
                if 'mia' not in content_str and 'zoe' not in content_str:
                    state["missing_slips_correct"] = True
                    
        except Exception:
            pass

    with open('state.json', 'w') as f:
        json.dump(state, f)

if __name__ == '__main__':
    verify()
