import os
import json
import glob

def verify():
    results = {
        "report_exists": False,
        "unauthorized_and_non_compliant_detected": False, # Should catch "Unknown Stranger", "Intruder Ivan", AND "Bob Johnson" (no waiver)
        "fully_authorized_math_accurate": False, # Only Alice and Charlie totals
        "skill_usage_correct": False
    }

    files = glob.glob("deliverables/*")
    if files:
        results["report_exists"] = True
        content = ""
        try:
            with open(files[0], "r") as f:
                content = f.read().lower()
            
            # 1. Check unauthorized/non-compliant
            # Bob Johnson is on whitelist but lacks waiver (based on skill logic)
            if "unknown stranger" in content and "intruder ivan" in content and "bob johnson" in content:
                results["unauthorized_and_non_compliant_detected"] = True
            
            # 2. Check Math for Fully Authorized (Alice and Charlie)
            # Alice: 4 (LogA) + 2 (LogB) = 6
            # Charlie: 2.5 (LogB)
            # Bob is excluded because of waiver status
            if "alice smith" in content and "6" in content:
                if "charlie brown" in content and "2.5" in content:
                    results["fully_authorized_math_accurate"] = True
        except:
            pass

    # Check Skill usage via state (this is usually supplemented by verify_prompt)
    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
