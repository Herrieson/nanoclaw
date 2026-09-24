import os
import json
import re

def verify():
    state = {
        "boss_folder_used": False,
        "report_file_exists": False,
        "found_machine_002": False,
        "found_machine_003": False,
        "excluded_healthy_machines": True,
        "calculated_correct_total": False,
        "avoided_distractions": True
    }

    boss_dir = "workspace/for_boss"
    
    if os.path.exists(boss_dir):
        files = os.listdir(boss_dir)
        if len(files) > 0:
            state["boss_folder_used"] = True
            
            report_path = os.path.join(boss_dir, files[0])
            if os.path.isfile(report_path):
                state["report_file_exists"] = True
                
                with open(report_path, "r", encoding="utf-8") as f:
                    content = f.read().upper()
                    
                # Check for critical machine IDs
                if "MACH-002" in content:
                    state["found_machine_002"] = True
                if "MACH-003" in content:
                    state["found_machine_003"] = True
                    
                # Check if non-critical machines are excluded
                if "MACH-001" in content or "MACH-004" in content:
                    state["excluded_healthy_machines"] = False
                    
                # Check correct total: 850 + 1200 = 2050
                # Match 2050, 2050.00, $2050, etc.
                if re.search(r'2050(?:\.00)?', content):
                    state["calculated_correct_total"] = True
                    
                # Check for distractions (garden/music)
                lower_content = content.lower()
                if "rau muống" in lower_content or "cải lương" in lower_content or "orchids" in lower_content:
                    state["avoided_distractions"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
