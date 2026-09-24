import os
import json

def verify():
    state = {
        "reports_folder_exists": False,
        "json_file_exists": False,
        "json_format_valid": False,
        "correct_kids_identified": False,
        "allergy_safety_verified": False,
        "dialect_skill_used": False
    }

    report_dir = "parent_reports"
    json_path = os.path.join(report_dir, "safe_garden_snacks.json")

    # Trace check for skill usage
    if os.path.exists("trace.jsonl"):
        with open("trace.jsonl", "r") as f:
            trace_content = f.read()
            if "dialect_to_standard_english_skill" in trace_content:
                state["dialect_skill_used"] = True

    if os.path.isdir(report_dir):
        state["reports_folder_exists"] = True

    if os.path.isfile(json_path):
        state["json_file_exists"] = True
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["json_format_valid"] = True
            
            # Expected: 
            # Noah (Peanuts + Garden + Celery=Safe)
            # Chloe (Gluten + Garden + Carrots=Safe)
            # Emma (Garden but NO allergy - task asks for kids with BOTH)
            # Liam (Allergy but NO garden)
            expected_keys = {"Noah", "Chloe"}
            actual_keys = set(data.keys())
            
            if actual_keys == expected_keys:
                state["correct_kids_identified"] = True
                
            if data.get("Noah") == "celery sticks" and data.get("Chloe") == "carrot sticks":
                state["allergy_safety_verified"] = True
        except:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
