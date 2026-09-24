import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# Configuration for LLM Judge
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    planning_dir = os.path.join(workspace, "planning")
    action_plan_path = os.path.join(planning_dir, "action_plan.md")
    gps_pins_path = os.path.join(planning_dir, "gps_pins.json")

    # 1. Check Directory and Files Existence (10 points)
    if os.path.exists(planning_dir) and os.path.isdir(planning_dir):
        score += 5
        details.append({"item": "Directory 'planning' exists", "score": 5, "max_score": 5, "passed": True})
        
        files_exist = os.path.exists(action_plan_path) and os.path.exists(gps_pins_path)
        if files_exist:
            score += 5
            details.append({"item": "Files action_plan.md and gps_pins.json exist", "score": 5, "max_score": 5, "passed": True})
        else:
            details.append({"item": "Files action_plan.md and gps_pins.json exist", "score": 0, "max_score": 5, "passed": False})
    else:
        details.append({"item": "Directory 'planning' exists", "score": 0, "max_score": 10, "passed": False})

    # 2. Verify gps_pins.json Content (40 points)
    # The golden records are T-1001 to T-1005 with specific KM markers.
    expected_pins = {
        "T-1001": 1.2,
        "T-1002": 5.5,
        "T-1003": 0.8,
        "T-1004": 12.4,
        "T-1005": 3.3
    }
    
    if os.path.exists(gps_pins_path):
        try:
            with open(gps_pins_path, 'r') as f:
                actual_pins = json.load(f)
            
            # Check for exact match of golden records
            correct_count = 0
            for tid, km in expected_pins.items():
                if tid in actual_pins and abs(float(actual_pins[tid]) - km) < 0.001:
                    correct_count += 1
            
            # Check for extra (incorrect) records (decoys or noise)
            extra_records = set(actual_pins.keys()) - set(expected_pins.keys())
            
            item_score = (correct_count / len(expected_pins)) * 40
            if extra_records:
                penalty = len(extra_records) * 5
                item_score = max(0, item_score - penalty)
                details.append({"item": "Verify gps_pins.json content", "score": int(item_score), "max_score": 40, "passed": item_score == 40, "reason": f"Found {correct_count} correct and {len(extra_records)} extra records."})
            else:
                details.append({"item": "Verify gps_pins.json content", "score": int(item_score), "max_score": 40, "passed": item_score == 40, "reason": f"Found {correct_count} correct records."})
            score += int(item_score)
        except Exception as e:
            details.append({"item": "Verify gps_pins.json content", "score": 0, "max_score": 40, "passed": False, "reason": f"JSON parse error: {e}"})

    # 3. Verify action_plan.md Table and Content (50 points)
    if os.path.exists(action_plan_path):
        with open(action_plan_path, 'r') as f:
            md_content = f.read()
        
        # 3a. Structural Check via LLM (20 points)
        table_check = llm_judge_content(
            "Does the file contain a clear visual table with Trail ID, KM, Issue, and Required Gear for the hazards?",
            md_content
        )
        if table_check:
            score += 20
            details.append({"item": "Markdown table structure check", "score": 20, "max_score": 20, "passed": True})
        else:
            details.append({"item": "Markdown table structure check", "score": 0, "max_score": 20, "passed": False})

        # 3b. Data Accuracy in Markdown via LLM (30 points)
        # We check if the Gear Mapping (Multi-hop) was done correctly.
        # HC-01 (Fallen Tree) -> Chainsaw & Winch
        # HC-03 (Mudslide) -> Heavy Excavator
        # HC-02 (Erosion) -> Shovels & Sandbags
        data_check_prompt = (
            "Check if the following records are present in the table with correct gear:\n"
            "1. T-1001 (Fallen Tree) needs 'Chainsaw & Winch'\n"
            "2. T-1002 (Mudslide) needs 'Heavy Excavator'\n"
            "3. T-1003 (Erosion) needs 'Shovels & Sandbags'\n"
            "4. T-1004 (Fallen Tree) needs 'Chainsaw & Winch'\n"
            "5. T-1005 (Mudslide) needs 'Heavy Excavator'\n"
            "Are ALL these present with correct gear? Answer YES or NO."
        )
        data_correct = llm_judge_content(data_check_prompt, md_content)
        if data_correct:
            score += 30
            details.append({"item": "Markdown table content accuracy (Gear mapping)", "score": 30, "max_score": 30, "passed": True})
        else:
            details.append({"item": "Markdown table content accuracy (Gear mapping)", "score": 0, "max_score": 30, "passed": False})

    # Final Output
    output = {
        "total_score": int(score),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    verify()
