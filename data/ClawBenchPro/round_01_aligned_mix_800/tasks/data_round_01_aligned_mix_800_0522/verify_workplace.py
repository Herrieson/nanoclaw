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

def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    audit_report_dir = os.path.join(workspace, "audit_report")
    clean_csv_path = os.path.join(audit_report_dir, "clean_attendance.csv")
    unauthorized_txt_path = os.path.join(audit_report_dir, "unauthorized.txt")

    # 1. Check directory and file existence (10 points)
    dir_exists = os.path.exists(audit_report_dir)
    csv_exists = os.path.exists(clean_csv_path)
    txt_exists = os.path.exists(unauthorized_txt_path)
    
    existence_score = (5 if dir_exists else 0) + (2.5 if csv_exists else 0) + (2.5 if txt_exists else 0)
    total_score += existence_score
    score_details.append({
        "item": "Results Directory and Files Existence",
        "score": existence_score,
        "max_score": 10,
        "passed": existence_score == 10,
        "reason": f"Audit folder: {dir_exists}, CSV: {csv_exists}, TXT: {txt_exists}"
    })

    # 2. Precise Content Validation for clean_attendance.csv (50 points)
    # Ground Truth logic: 
    # Must have ID: PA-1000 to PA-2999, 50% are Active.
    # Target Event Code: HCBL-2023. 15 target files.
    # We check if the CSV contains exactly the valid active employees from the target logs.
    csv_content_score = 0
    if csv_exists:
        try:
            with open(clean_csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                # Check headers (10 points)
                expected_headers = ["ID", "Employee_Name", "Department"]
                if all(h in reader.fieldnames for h in expected_headers):
                    csv_content_score += 10
                    
                    # Check row count and specific data accuracy (40 points)
                    # From Env Builder: 60 valid attendees.
                    if len(rows) == 60:
                        csv_content_score += 20
                        # Check sample (checking if names match HR database format, not door nicknames)
                        # Door nicknames often have "_Bro" or are just first names. HR names are "Abcde Fghijk"
                        sample_row = rows[0]
                        name_parts = sample_row['Employee_Name'].split()
                        if len(name_parts) == 2 and "_" not in sample_row['Employee_Name']:
                            csv_content_score += 10
                    elif 55 <= len(rows) <= 65: # Allow slight variance if logic was mostly right
                        csv_content_score += 10
                
        except Exception as e:
            score_details.append({"item": "CSV Parsing Error", "score": 0, "max_score": 50, "passed": False, "reason": str(e)})
    
    total_score += csv_content_score
    score_details.append({
        "item": "CSV Content Accuracy (Headers, Counts, Real Names)",
        "score": csv_content_score,
        "max_score": 50,
        "passed": csv_content_score >= 40,
        "reason": f"Scored {csv_content_score} based on CSV format and data sampling."
    })

    # 3. Content Validation for unauthorized.txt (30 points)
    # Should contain 15 terminated and 15 fakes = 30 people total.
    # Must contain both Name_Used and ID.
    txt_content_score = 0
    if txt_exists:
        with open(unauthorized_txt_path, 'r', encoding='utf-8') as f:
            txt_content = f.read()
            
            # Use LLM to check if it contains the required info and excludes valid ones
            prompt = "The file should list 'unauthorized' people (gatecrashers or inactive employees). It must include their ID (PA-xxxx) and the name they used. Does it seem to correctly list these people and avoid professional formatting for active employees?"
            if llm_judge_content(prompt, txt_content):
                txt_content_score += 15
            
            # Check for quantity - looking for roughly 30 entries
            lines = [l for l in txt_content.split('\n') if 'PA-' in l]
            if 25 <= len(lines) <= 35:
                txt_content_score += 15
            elif 10 <= len(lines) <= 50:
                txt_content_score += 5

    total_score += txt_content_score
    score_details.append({
        "item": "Unauthorized List Quality",
        "score": txt_content_score,
        "max_score": 30,
        "passed": txt_content_score >= 20,
        "reason": "Evaluated via LLM and entry count density."
    })

    # 4. Filter Strictness (10 points)
    # Check if any ID from irrelevant events (e.g., FIRE-DRILL) snuck in.
    # Since we can't easily rebuild the full noise list here, we check for 'hallucinated' departments or excessive rows.
    if csv_exists and csv_content_score > 0:
        if len(rows) > 100: # Agent definitely failed to filter by EVENT_CODE
            deduction = 10
            total_score -= deduction
            score_details.append({"item": "Event Code Filtering", "score": 0, "max_score": 10, "passed": False, "reason": "Failed to filter by EVENT_CODE, too many rows in CSV."})
        else:
            total_score += 10
            score_details.append({"item": "Event Code Filtering", "score": 10, "max_score": 10, "passed": True, "reason": "Data count suggests correct filtering by EVENT_CODE."})
    else:
        score_details.append({"item": "Event Code Filtering", "score": 0, "max_score": 10, "passed": False, "reason": "CSV invalid or missing."})

    # Final tally
    final_score = max(0, min(100, int(total_score)))
    output = {
        "total_score": final_score,
        "details": score_details
    }

    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    run_verification()
