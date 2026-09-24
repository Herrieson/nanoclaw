import os
import json
import sys

def verify():
    # Objective state probe
    state = {
        "deliverables_folder_exists": False,
        "final_roster_exists": False,
        "valid_json_format": False,
        "has_correct_structure": False,
        "leo_correct_instructor": False,    # Needs Guitar + SpEd (Sarah)
        "mia_correct_instructor": False,    # Needs Piano + SpEd (Elena)
        "sam_correct_instructor": False,    # Needs Drums + SpEd (Joao)
        "noah_correct_instructor": False,   # Needs Piano + SpEd (Elena)
        "mateo_correct_instructor": False,  # Needs Bass + SpEd (Sarah)
        "lucas_is_unmatched": False,        # Needs Violin + SpEd (No Violin teacher at all)
        "emma_is_matched": False,           # Normal Guitar (David or Sarah)
        "zoe_is_matched": False             # Normal Drums (Miguel or Joao)
    }

    target_path = "deliverables/final_roster.json"

    if os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True

    if os.path.isfile(target_path):
        state["final_roster_exists"] = True
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            state["valid_json_format"] = True

            # Check structure
            if "matched" in data and "unmatched" in data:
                if isinstance(data["matched"], list) and isinstance(data["unmatched"], list):
                    state["has_correct_structure"] = True
                    
                    matched_dict = {}
                    for match in data["matched"]:
                        # Handle variations in key names (student_name, student, etc.)
                        student = match.get("student_name", match.get("student", match.get("name", "")))
                        instructor = match.get("instructor_name", match.get("instructor", ""))
                        if student and instructor:
                            matched_dict[student.strip()] = instructor.strip()

                    unmatched_list = [str(u).strip() for u in data["unmatched"]]

                    # Check SpEd Matches
                    if matched_dict.get("Leo") == "Sarah": state["leo_correct_instructor"] = True
                    if matched_dict.get("Mia") == "Elena": state["mia_correct_instructor"] = True
                    if matched_dict.get("Sam") == "Joao": state["sam_correct_instructor"] = True
                    if matched_dict.get("Noah") == "Elena": state["noah_correct_instructor"] = True
                    if matched_dict.get("Mateo") == "Sarah": state["mateo_correct_instructor"] = True

                    # Check Unmatched
                    if "Lucas" in unmatched_list or any(isinstance(u, dict) and u.get("student_name") == "Lucas" for u in data["unmatched"]):
                        state["lucas_is_unmatched"] = True

                    # Check Normal Matches
                    if "Emma" in matched_dict and matched_dict.get("Emma") in ["David", "Sarah"]: 
                        state["emma_is_matched"] = True
                    if "Zoe" in matched_dict and matched_dict.get("Zoe") in ["Miguel", "Joao"]: 
                        state["zoe_is_matched"] = True

        except Exception:
            pass # Invalid JSON or unexpected format

    # Dump state to a physical file
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
