import os
import sys
import json
import glob
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def check_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []

    # 1. Check if the dashboard_api directory exists
    target_dir = os.path.join(workspace, "dashboard_api")
    if os.path.isdir(target_dir):
        total_score += 10
        details.append({"item": "Directory Structure", "score": 10, "max_score": 10, "passed": True, "reason": "`dashboard_api` directory created successfully."})
    else:
        details.append({"item": "Directory Structure", "score": 0, "max_score": 10, "passed": False, "reason": "`dashboard_api` directory is missing."})

    # 2. Check for the existence and validity of JSON file
    parsed_data = None
    if os.path.isdir(target_dir):
        json_files = glob.glob(os.path.join(target_dir, "*.json"))
        if len(json_files) > 0:
            for jf in json_files:
                try:
                    with open(jf, "r", encoding="utf-8") as f:
                        parsed_data = json.load(f)
                    total_score += 10
                    details.append({"item": "JSON Validity", "score": 10, "max_score": 10, "passed": True, "reason": f"Found valid JSON file: {os.path.basename(jf)}"})
                    break
                except Exception:
                    pass
            if parsed_data is None:
                details.append({"item": "JSON Validity", "score": 0, "max_score": 10, "passed": False, "reason": "Found JSON files, but none could be parsed (invalid format)."})
        else:
            details.append({"item": "JSON Validity", "score": 0, "max_score": 10, "passed": False, "reason": "No JSON files found in the `dashboard_api` directory."})
    else:
        details.append({"item": "JSON Validity", "score": 0, "max_score": 10, "passed": False, "reason": "Skipped because `dashboard_api` directory does not exist."})

    # Helper function to extract all values from parsed JSON regardless of keys
    def extract_values(obj):
        vals = []
        if isinstance(obj, dict):
            for v in obj.values():
                vals.extend(extract_values(v))
        elif isinstance(obj, list):
            for item in obj:
                vals.extend(extract_values(item))
        else:
            vals.append(obj)
        return vals

    # Check exact values
    fuel_found = False
    miles_found = False
    city_found = False

    if parsed_data is not None:
        flat_values = extract_values(parsed_data)
        
        floats_and_ints = [float(v) for v in flat_values if isinstance(v, (int, float))]
        strings = [str(v).lower() for v in flat_values if isinstance(v, str)]

        # 3. Exact Check: Total Fuel Expenses (Valid fuel receipts sum to exactly 1317.25)
        # We allow a very small epsilon for float variations
        for val in floats_and_ints:
            if abs(val - 1317.25) < 0.01:
                fuel_found = True
                break
        
        if fuel_found:
            total_score += 25
            details.append({"item": "Total Fuel Expenses", "score": 25, "max_score": 25, "passed": True, "reason": "Correct total fuel expenses (1317.25) strictly matched."})
        else:
            details.append({"item": "Total Fuel Expenses", "score": 0, "max_score": 25, "passed": False, "reason": "Did not find the exact calculated sum of fuel expenses."})

        # 4. Exact Check: Total Miles Driven (Valid firmwares sum to exactly 3464.5)
        for val in floats_and_ints:
            if abs(val - 3464.5) < 0.01:
                miles_found = True
                break
        
        if miles_found:
            total_score += 25
            details.append({"item": "Total Miles Driven", "score": 25, "max_score": 25, "passed": True, "reason": "Correct total miles (3464.5) strictly matched."})
        else:
            details.append({"item": "Total Miles Driven", "score": 0, "max_score": 25, "passed": False, "reason": "Did not find the exact calculated sum of valid miles."})

        # 5. Exact Check: Longest Idle City (Gary, IN)
        for val in strings:
            if "gary" in val and "in" in val:
                city_found = True
                break
        
        if city_found:
            total_score += 30
            details.append({"item": "Longest Idle City", "score": 30, "max_score": 30, "passed": True, "reason": "Correct longest idle city (Gary, IN) strictly matched."})
        else:
            details.append({"item": "Longest Idle City", "score": 0, "max_score": 30, "passed": False, "reason": "Did not find the correct longest idle city name."})
    else:
        details.append({"item": "Total Fuel Expenses", "score": 0, "max_score": 25, "passed": False, "reason": "Cannot check due to missing/invalid JSON."})
        details.append({"item": "Total Miles Driven", "score": 0, "max_score": 25, "passed": False, "reason": "Cannot check due to missing/invalid JSON."})
        details.append({"item": "Longest Idle City", "score": 0, "max_score": 30, "passed": False, "reason": "Cannot check due to missing/invalid JSON."})

    # Write the result report
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=4)

if __name__ == "__main__":
    check_workplace()
