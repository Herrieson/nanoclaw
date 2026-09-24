import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# Configuration for LLM
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
    party_plan_dir = os.path.join(workspace, "party_plan")
    results = []
    total_score = 0

    # 1. Directory Structure (10 points)
    dir_exists = os.path.exists(party_plan_dir) and os.path.isdir(party_plan_dir)
    results.append({
        "item": "Directory 'party_plan' exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Found party_plan directory" if dir_exists else "Directory party_plan missing"
    })
    if dir_exists:
        total_score += results[-1]["score"]

    # 2. File Presence & Format (10 points)
    report_file = None
    if dir_exists:
        files = [f for f in os.listdir(party_plan_dir) if os.path.isfile(os.path.join(party_plan_dir, f))]
        if files:
            report_file = os.path.join(party_plan_dir, files[0])
            results.append({
                "item": "Summary report file exists",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"Found report file: {files[0]}"
            })
            total_score += 10
        else:
            results.append({
                "item": "Summary report file exists",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "No files found in party_plan"
            })

    # 3. Data Validation - Whitelist Logic (40 points)
    # Correct calculation:
    # Whitelist: Chad, Big Mike, Father Tom, Gunner, Dave from Receiving
    # RSVPs matching:
    # Chad (1 +1) = 2
    # Big Mike (3 +1) = 4
    # Gunner (0 +1) = 1
    # Father Tom (0 +1) = 1
    # Dave (2 +1) = 3
    # Total Attendees = 2 + 4 + 1 + 1 + 3 = 11
    # Food: Burgers=22, Hotdogs=11, Beers=44
    # Note: Sneaky Pete and Gym Bro Steve must be excluded.
    
    expected_attendees = 11
    expected_burgers = 22
    expected_hotdogs = 11
    expected_beers = 44

    if report_file:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for crashers
        crasher_check = "Sneaky Pete" not in content and "Gym Bro Steve" not in content
        results.append({
            "item": "Exclusion of non-whitelist crashers",
            "score": 20 if crasher_check else 0,
            "max_score": 20,
            "passed": crasher_check,
            "reason": "Correctly filtered out Sneaky Pete and Gym Bro Steve" if crasher_check else "Failed to exclude unauthorized guests"
        })
        if crasher_check: total_score += 20

        # Check math accuracy via code (Extracting numbers)
        import re
        burgers_found = re.findall(r'(\d+)\s*burgers?', content, re.IGNORECASE)
        hotdogs_found = re.findall(r'(\d+)\s*hotdogs?', content, re.IGNORECASE)
        beers_found = re.findall(r'(\d+)\s*beers?', content, re.IGNORECASE)
        
        math_correct = False
        if burgers_found and hotdogs_found and beers_found:
            if int(burgers_found[0]) == expected_burgers and \
               int(hotdogs_found[0]) == expected_hotdogs and \
               int(beers_found[0]) == expected_beers:
                math_correct = True
        
        results.append({
            "item": "Calculation accuracy (Burgers/Hotdogs/Beers)",
            "score": 20 if math_correct else 0,
            "max_score": 20,
            "passed": math_correct,
            "reason": f"Expected {expected_burgers}/{expected_hotdogs}/{expected_beers}, extracted {burgers_found}/{hotdogs_found}/{beers_found}"
        })
        if math_correct: total_score += 20

        # 4. LLM Tone & Clarity Check (40 points)
        tone_prompt = "Verify if the text is a 'nice, clean summary report' suitable for a manager. It should list clear totals for food and avoid messy raw logs. Is it professional and organized?"
        tone_passed = llm_judge_content(tone_prompt, content)
        results.append({
            "item": "Report professionalism and clarity (LLM Judge)",
            "score": 40 if tone_passed else 10,
            "max_score": 40,
            "passed": tone_passed,
            "reason": "Report is clean and professional" if tone_passed else "Report is messy or poorly formatted"
        })
        if tone_passed: total_score += 40
        else: total_score += 10 # Partial for attempt

    # Output final score
    output = {
        "total_score": int(total_score),
        "details": results
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    verify()
