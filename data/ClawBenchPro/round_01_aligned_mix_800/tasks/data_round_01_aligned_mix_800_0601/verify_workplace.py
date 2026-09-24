import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    deliverables_dir = os.path.join(workspace, "deliverables")
    roster_path = os.path.join(deliverables_dir, "final_roster.json")

    # 1. Directory and File Existence (10 pts)
    if os.path.isdir(deliverables_dir) and os.path.isfile(roster_path):
        score += 10
        details.append({"item": "Directory and File Existence", "score": 10, "max_score": 10, "passed": True, "reason": "final_roster.json exists in deliverables directory"})
    else:
        details.append({"item": "Directory and File Existence", "score": 0, "max_score": 10, "passed": False, "reason": "final_roster.json does not exist"})
        
        # Immediate fail if output doesn't exist
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, indent=4)
        return

    # 2. JSON Structure Valid (10 pts)
    try:
        with open(roster_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        has_matched = "matched" in data and isinstance(data["matched"], list)
        has_unmatched = "unmatched" in data and isinstance(data["unmatched"], list)

        if has_matched and has_unmatched:
            score += 10
            details.append({"item": "JSON Structure", "score": 10, "max_score": 10, "passed": True, "reason": "Properly contains 'matched' and 'unmatched' arrays"})
        else:
            details.append({"item": "JSON Structure", "score": 0, "max_score": 10, "passed": False, "reason": "Missing 'matched' or 'unmatched' top-level keys as lists"})
            with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
                json.dump({"total_score": score, "details": details}, f, indent=4)
            return
    except Exception as e:
        details.append({"item": "JSON Structure", "score": 0, "max_score": 10, "passed": False, "reason": f"File is not valid JSON: {str(e)}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, indent=4)
        return

    # 3. Unmatched Verification (20 pts)
    # Lucas needs a Violin teacher with Special Ed. None exists.
    unmatched = data["unmatched"]
    # Safely extract names if agent wrapped them in dicts instead of plain strings
    unmatched_names = [str(x).lower().strip() if isinstance(x, str) else str(x.get('name', x.get('student_name', ''))).lower().strip() for x in unmatched]
    
    if len(unmatched_names) == 1 and "lucas" in unmatched_names[0]:
        score += 20
        details.append({"item": "Unmatched Group", "score": 20, "max_score": 20, "passed": True, "reason": "Lucas correctly identified as the sole unmatched student"})
    else:
        details.append({"item": "Unmatched Group", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected exactly 'Lucas' unmatched, found: {unmatched_names}"})

    # Parse matched data
    matched = data["matched"]
    student_to_instructor = {}
    for item in matched:
        if isinstance(item, dict):
            student = None
            instructor = None
            for k in ["student_name", "student", "name", "child"]:
                if k in item:
                    student = str(item[k]).lower().strip()
                    break
            for k in ["instructor_name", "instructor", "teacher", "assigned_instructor", "staff"]:
                if k in item:
                    instructor = str(item[k]).lower().strip()
                    break
            if student and instructor:
                student_to_instructor[student] = instructor

    # 4. Matched List Size (10 pts)
    if len(student_to_instructor) == 8:
        score += 10
        details.append({"item": "Matched Size", "score": 10, "max_score": 10, "passed": True, "reason": "Exactly 8 students matched"})
    else:
        details.append({"item": "Matched Size", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 8 matches, found {len(student_to_instructor)}"})

    # 5. Special Needs Assignments (30 pts)
    special_needs_matches = {
        "leo": "sarah",     # Guitar, Sensory -> Sarah (SpecEd)
        "mia": "elena",     # Piano, Wheelchair -> Elena (SpecEd)
        "sam": "joao",      # Drums, ADHD -> Joao (SpecEd)
        "noah": "elena",    # Piano, Sensory -> Elena (SpecEd)
        "mateo": "sarah"    # Bass, Wheelchair -> Sarah (SpecEd)
    }

    special_score = 0
    special_failed_details = []
    for student, expected_instructor in special_needs_matches.items():
        found = False
        for s_key, i_val in student_to_instructor.items():
            if student in s_key:
                found = True
                if expected_instructor in i_val:
                    special_score += 6
                else:
                    special_failed_details.append(f"{student} assigned {i_val} instead of {expected_instructor}")
                break
        if not found:
            special_failed_details.append(f"{student} missing from matches")
            
    score += special_score
    if special_score == 30:
        details.append({"item": "Special Needs Matches", "score": 30, "max_score": 30, "passed": True, "reason": "All 5 special needs students matched with Special Ed instructors accurately"})
    else:
        details.append({"item": "Special Needs Matches", "score": special_score, "max_score": 30, "passed": False, "reason": "; ".join(special_failed_details)})

    # 6. Regular Assignments (20 pts)
    regular_matches = {
        "emma": ["david", "sarah"],
        "chloe": ["elena", "david"],
        "zoe": ["miguel", "joao"]
    }
    
    reg_score = 0
    reg_failed_details = []
    for student, allowed_instructors in regular_matches.items():
        found = False
        for s_key, i_val in student_to_instructor.items():
            if student in s_key:
                found = True
                if any(ins in i_val for ins in allowed_instructors):
                    reg_score += 6
                    if student == "emma" or student == "chloe":
                        reg_score += 1 # Distribution to make exact 20 points
                else:
                    reg_failed_details.append(f"{student} assigned {i_val} which is invalid for instrument")
                break
        if not found:
            reg_failed_details.append(f"{student} missing from matches")
            
    score += reg_score
    if reg_score == 20:
        details.append({"item": "Regular Matches", "score": 20, "max_score": 20, "passed": True, "reason": "All 3 regular students matched with correct instrument instructors"})
    else:
        details.append({"item": "Regular Matches", "score": reg_score, "max_score": 20, "passed": False, "reason": "; ".join(reg_failed_details)})

    # Save final score
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, indent=4)

if __name__ == "__main__":
    main()
