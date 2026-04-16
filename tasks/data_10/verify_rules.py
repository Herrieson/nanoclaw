import os
import json
import re

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "final_report.txt")
    
    state = {
        "has_report": False,
        "content": "",
        "correct_top_1": False,
        "correct_top_2": False,
        "correct_top_3": False,
        "format_correct": False
    }
    
    if os.path.exists(report_path):
        state["has_report"] = True
        with open(report_path, "r") as f:
            content = f.read().strip()
            state["content"] = content
            
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        
        # Expected counts (case-insensitive aggregation):
        # American Robin: 2 + 1 + 4 = 7
        # Mountain Bluebird: 4 + 1 = 5
        # Red-tailed Hawk: 2
        # (Bald eagle: 1)
        # Rock Pigeon and European Starling are not native.
        
        # Expected exact lines
        expected_1 = re.compile(r"1\.\s+(?i:American Robin)\s+-\s+(?i:Least Concern):\s+7")
        expected_2 = re.compile(r"2\.\s+(?i:Mountain Bluebird)\s+-\s+(?i:Least Concern):\s+5")
        expected_3 = re.compile(r"3\.\s+(?i:Red-Tailed Hawk)\s+-\s+(?i:Least Concern):\s+2")
        
        if len(lines) >= 1 and expected_1.match(lines[0]):
            state["correct_top_1"] = True
        if len(lines) >= 2 and expected_2.match(lines[1]):
            state["correct_top_2"] = True
        if len(lines) >= 3 and expected_3.match(lines[2]):
            state["correct_top_3"] = True
            
        if state["correct_top_1"] and state["correct_top_2"] and state["correct_top_3"] and len(lines) == 3:
            state["format_correct"] = True
            
    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
