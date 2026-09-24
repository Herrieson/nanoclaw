import os
import sys
import json

def verify_task():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "briefing/poachers_report.txt")
    score = 0
    details = []

    # 1. Check if the report file exists
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "Report file existence", "score": 10, "max_score": 10, "passed": True, "reason": "File briefing/poachers_report.txt exists."})
    else:
        details.append({"item": "Report file existence", "score": 0, "max_score": 10, "passed": False, "reason": "File briefing/poachers_report.txt not found."})
        # If file doesn't exist, we stop early or continue with 0 for other items
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 2. Read and clean the report content
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        # Ground Truth Logic:
        # Plates from 14:15 incident: 
        # CA-5GTR222 (VALID) -> No
        # CA-9FAKE00 (MISSING) -> YES
        # CA-1ABC123 (EXPIRED) -> YES
        # CA-BAD888 (SUSPENDED) -> YES
        # CA-8HJK999 (VALID) -> No
        # Decoy from 09:00:
        # CA-NORM111 (VALID) -> No
        
        expected_plates = {"CA-9FAKE00", "CA-1ABC123", "CA-BAD888"}
        incorrect_decoys = {"CA-5GTR222", "CA-8HJK999", "CA-NORM111"}
        
        found_plates = set(lines)
        
        # 3. Check for correct plates (30 points each)
        for plate in expected_plates:
            if plate in found_plates:
                score += 25
                details.append({"item": f"Identify poacher {plate}", "score": 25, "max_score": 25, "passed": True, "reason": f"Correctly identified {plate}"})
            else:
                details.append({"item": f"Identify poacher {plate}", "score": 0, "max_score": 25, "passed": False, "reason": f"Failed to identify {plate}"})
        
        # 4. Check for hallucinations/decoys (Deduction)
        extra_plates = found_plates - expected_plates
        if not extra_plates:
            score += 15
            details.append({"item": "No false positives", "score": 15, "max_score": 15, "passed": True, "reason": "No incorrect plates included."})
        else:
            # Harsh penalty for including decoys or non-incident plates
            penalty = len(extra_plates) * 10
            actual_bonus = max(0, 15 - penalty)
            score += actual_bonus
            details.append({"item": "No false positives", "score": actual_bonus, "max_score": 15, "passed": False, "reason": f"Included incorrect plates: {list(extra_plates)}"})

    except Exception as e:
        details.append({"item": "File parsing", "score": 0, "max_score": 90, "passed": False, "reason": f"Error parsing report: {str(e)}"})

    # Final score cap
    total_score = max(0, min(100, score))
    
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(total_score), "details": details}, f)

if __name__ == "__main__":
    verify_task()
