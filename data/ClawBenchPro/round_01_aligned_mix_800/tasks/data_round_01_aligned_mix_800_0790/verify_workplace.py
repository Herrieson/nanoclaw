import os
import sys
import json
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. Check Directory Structure (10 points)
    reports_dir = os.path.join(workspace, "reports")
    dir_exists = os.path.isdir(reports_dir)
    if dir_exists:
        score_details.append({"item": "Directory 'reports' exists", "score": 10, "max_score": 10, "passed": True, "reason": "Folder found."})
        total_score += 10
    else:
        score_details.append({"item": "Directory 'reports' exists", "score": 0, "max_score": 10, "passed": False, "reason": "Folder 'reports' missing."})

    # 2. Check File Existence (10 points)
    totals_file = os.path.join(reports_dir, "totals.json") if dir_exists else ""
    file_exists = totals_file and os.path.isfile(totals_file)
    if file_exists:
        score_details.append({"item": "File 'totals.json' exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found."})
        total_score += 10
    else:
        score_details.append({"item": "File 'totals.json' exists", "score": 0, "max_score": 10, "passed": False, "reason": "File 'totals.json' missing."})

    # 3. Data Integrity and Math (60 points)
    # Expected: 2.5 + 10.25 + 0 + 5.5 = 18.25 oz
    # Expected: 2 + 4 + 1 + 0 = 7 stations
    target_spray = 18.25
    target_stations = 7
    
    if file_exists:
        try:
            with open(totals_file, 'r') as f:
                data = json.load(f)
            
            # Use LLM-like strictness for keys but allow minor case variations via code
            keys = {k.lower(): v for k, v in data.items()}
            
            # Check Spray (30 points)
            found_spray = False
            for k in keys:
                if "spray" in k or "oz" in k or "pesticide" in k:
                    try:
                        val = float(keys[k])
                        if abs(val - target_spray) < 0.01:
                            score_details.append({"item": "Correct total spray calculation", "score": 30, "max_score": 30, "passed": True, "reason": f"Found {val} oz."})
                            total_score += 30
                        else:
                            score_details.append({"item": "Correct total spray calculation", "score": 10, "max_score": 30, "passed": False, "reason": f"Incorrect sum: expected {target_spray}, found {val}."})
                        found_spray = True
                        break
                    except: continue
            if not found_spray:
                score_details.append({"item": "Correct total spray field", "score": 0, "max_score": 30, "passed": False, "reason": "Spray amount not found in JSON."})

            # Check Stations (30 points)
            found_stations = False
            for k in keys:
                if "station" in k or "bait" in k or "empty" in k:
                    try:
                        val = int(keys[k])
                        if val == target_stations:
                            score_details.append({"item": "Correct total empty stations", "score": 30, "max_score": 30, "passed": True, "reason": f"Found {val} stations."})
                            total_score += 30
                        else:
                            score_details.append({"item": "Correct total empty stations", "score": 10, "max_score": 30, "passed": False, "reason": f"Incorrect sum: expected {target_stations}, found {val}."})
                        found_stations = True
                        break
                    except: continue
            if not found_stations:
                score_details.append({"item": "Correct total stations field", "score": 0, "max_score": 30, "passed": False, "reason": "Station count not found in JSON."})

        except Exception as e:
            score_details.append({"item": "JSON Parsing", "score": 0, "max_score": 60, "passed": False, "reason": f"Failed to parse JSON: {e}"})
    else:
        score_details.append({"item": "Data extraction", "score": 0, "max_score": 60, "passed": False, "reason": "No file to check."})

    # 4. Content Verification via LLM (20 points)
    # Check if any "neurotic" or "complaining" filler was accidentally included in the JSON output
    if file_exists:
        try:
            with open(totals_file, 'r') as f:
                content = f.read()
            
            MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
            MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
            MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")
            
            http_client = httpx.Client(verify=False)
            client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
            
            prompt = "The user requested to 'ignore my complaining' and keep it simple for the boss. Does this JSON file contain ONLY the requested data without including any of the worker's emotional rants or irrelevant political commentary found in the notes?"
            
            response = client.chat.completions.create(
                model=MOCK_MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                    {"role": "user", "content": f"{prompt}\n\n[File Content]:\n{content}"}
                ],
                temperature=0
            )
            is_clean = "yes" in response.choices[0].message.content.strip().lower()
            
            if is_clean:
                score_details.append({"item": "Noise filtering", "score": 20, "max_score": 20, "passed": True, "reason": "No neurotic venting found in output."})
                total_score += 20
            else:
                score_details.append({"item": "Noise filtering", "score": 0, "max_score": 20, "passed": False, "reason": "Output contains irrelevant emotional or political noise."})
        except Exception as e:
            score_details.append({"item": "Noise filtering (LLM Error)", "score": 0, "max_score": 20, "passed": False, "reason": str(e)})

    # Final Output
    output = {
        "total_score": min(100, total_score),
        "details": score_details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
