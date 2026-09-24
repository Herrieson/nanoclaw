import os
import json
import sys

def verify():
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(base_dir, "deliverables")
    report_path = os.path.join(deliverables_dir, "official_safety_report.json")
    
    state = {
        "report_exists": False,
        "valid_json": False,
        "correct_total_hours": False,
        "found_scaffolding": False,
        "found_wiring": False,
        "found_hardhats": False,
        "found_trench": False,
        "ignored_crayon": True,
        "ignored_easel": True,
        "used_ocr_tool": False,
        "used_lookup_tool": False
    }

    # Check for tool usage in trace would be in verify_prompt, 
    # but we can check if they attempted to read the internal DB or other markers
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            # 14+20+8+22+16 = 80
            def find_80(obj):
                if isinstance(obj, (int, float)) and obj == 80: return True
                if isinstance(obj, str) and "80" in obj: return True
                if isinstance(obj, dict): return any(find_80(v) for v in obj.values())
                if isinstance(obj, list): return any(find_80(i) for i in obj)
                return False
            
            state["correct_total_hours"] = find_80(data)
            dumped_str = json.dumps(data).lower()
            
            # Hazards (only site ones)
            state["found_scaffolding"] = "scaffold" in dumped_str or "guardrail" in dumped_str
            state["found_wiring"] = "wir" in dumped_str or "water" in dumped_str
            state["found_hardhats"] = "hat" in dumped_str or "drop zone" in dumped_str
            state["found_trench"] = "trench" in dumped_str or "6 feet" in dumped_str
                
            # Distractors
            if any(x in dumped_str for x in ["crayon", "toddler", "easel", "paint", "mural"]):
                state["ignored_crayon"] = False # Shared flag for simplicity
        except:
            pass

    with open(os.path.join(base_dir, "state.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
