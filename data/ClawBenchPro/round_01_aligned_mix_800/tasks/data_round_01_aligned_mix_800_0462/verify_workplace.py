import os
import sys
import json
import httpx
from openai import OpenAI

# Configuration for potential LLM usage (though this task is primarily structured data)
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def verify_task():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports/daily_briefing.json")
    
    score = 0
    details = []

    # 1. Basic Structure Check (10 points)
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "Check report existence", "score": 10, "max_score": 10, "passed": True, "reason": "Report file exists."})
    else:
        details.append({"item": "Check report existence", "score": 0, "max_score": 10, "passed": False, "reason": "File reports/daily_briefing.json not found."})
        # If the file doesn't exist, we can't proceed with deep content checks
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 2. JSON Validity Check (10 points)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        score += 10
        details.append({"item": "Check JSON validity", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON format."})
    except Exception as e:
        details.append({"item": "Check JSON validity", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse JSON: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 3. Content Validation - Stolen Spotted Plates (40 points)
    # Expected: ["NVR-0012", "BKL-1002"]
    # Logic: FAL-9921 is RECOVERED. GLX-8443 was spotted yesterday.
    expected_stolen = {"NVR-0012", "BKL-1002"}
    actual_stolen = set(data.get("stolen_spotted", []))
    
    if actual_stolen == expected_stolen:
        score += 40
        details.append({"item": "Validate stolen spotted plates", "score": 40, "max_score": 40, "passed": True, "reason": "Correctly identified currently stolen plates seen today."})
    elif actual_stolen.issubset(expected_stolen) and len(actual_stolen) > 0:
        score += 20
        details.append({"item": "Validate stolen spotted plates", "score": 20, "max_score": 40, "passed": False, "reason": f"Partially correct. Found {actual_stolen}, missing some or included none."})
    else:
        # Check for specific "traps"
        reasons = []
        if "FAL-9921" in actual_stolen: reasons.append("Included RECOVERED vehicle FAL-9921")
        if "GLX-8443" in actual_stolen: reasons.append("Included vehicle from yesterday GLX-8443")
        reason_str = " | ".join(reasons) if reasons else "Incorrect plate list."
        details.append({"item": "Validate stolen spotted plates", "score": 0, "max_score": 40, "passed": False, "reason": reason_str})

    # 4. Content Validation - Worst Hotspot (40 points)
    # Expected: "Valley Highway Exit" (CAM_07)
    # Trap: CAM_02 (Downtown Avenue) has high speeds but is STAT: TEST.
    # Trap: CAM_03 (Mile Marker 42) has 25 speeders, CAM_07 has 45.
    expected_hotspot = "Valley Highway Exit"
    actual_hotspot = data.get("worst_hotspot", "")

    if actual_hotspot == expected_hotspot:
        score += 40
        details.append({"item": "Validate speeding hotspot", "score": 40, "max_score": 40, "passed": True, "reason": "Correctly identified Valley Highway Exit as the worst hotspot."})
    elif "Downtown" in actual_hotspot or "CAM_02" in actual_hotspot:
        details.append({"item": "Validate speeding hotspot", "score": 0, "max_score": 40, "passed": False, "reason": "Failed trap: Identified CAM_02 (TEST data) as hotspot."})
    elif "Mile Marker" in actual_hotspot or "CAM_03" in actual_hotspot:
        details.append({"item": "Validate speeding hotspot", "score": 10, "max_score": 40, "passed": False, "reason": "Incorrect: Identified the secondary hotspot (CAM_03) instead of the primary (CAM_07)."})
    else:
        details.append({"item": "Validate speeding hotspot", "score": 0, "max_score": 40, "passed": False, "reason": f"Expected '{expected_hotspot}', got '{actual_hotspot}'."})

    # Final score output
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(score), "details": details}, f)

if __name__ == "__main__":
    verify_task()
