import os
import json
import re

def verify():
    result = {
        "file_exists": False,
        "correct_format": False,
        "correct_count": False,
        "correct_order": False,
        "no_distractors": True
    }
    
    target_file = "timeline_evidence.md"
    
    if not os.path.exists(target_file):
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return
        
    result["file_exists"] = True
    
    expected_order = [
        "2023-10-20 22:30:00",
        "2023-10-21 09:15:00",
        "2023-10-22 14:20:00",
        "2023-10-23 18:45:00",
        "2023-10-25 08:10:00"
    ]
    
    extracted_times = []
    valid_lines_count = 0
    has_bad_format = False
    
    with open(target_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        
        for line in lines:
            # Check format: [YYYY-MM-DD HH:MM:SS] Sender -> Receiver: Message
            match = re.match(r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+(.*?)\s+->\s+(.*?):\s+(.*)$', line)
            if match:
                time, sender, receiver, msg = match.groups()
                extracted_times.append(time)
                
                # Check for distractors
                if sender not in ["CEO_John", "Admin_Sarah"] or receiver not in ["CEO_John", "Admin_Sarah"]:
                    result["no_distractors"] = False
                if "titanium breach" not in msg.lower():
                    result["no_distractors"] = False
                
                valid_lines_count += 1
            else:
                has_bad_format = True

    if not has_bad_format and valid_lines_count > 0:
        result["correct_format"] = True
        
    if valid_lines_count == 5:
        result["correct_count"] = True
        
    if extracted_times == expected_order:
        result["correct_order"] = True

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
