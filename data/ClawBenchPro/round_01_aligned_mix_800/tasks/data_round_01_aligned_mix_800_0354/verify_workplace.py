import os
import sys
import json
import csv
import httpx
from datetime import datetime
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

def parse_time(time_str):
    time_str = time_str.strip().upper()
    try:
        if "AM" in time_str or "PM" in time_str:
            return datetime.strptime(time_str, "%I:%M %p")
        else:
            return datetime.strptime(time_str, "%H:%M")
    except ValueError:
        return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    processed_dir = os.path.join(workspace, "processed")
    csv_file = os.path.join(processed_dir, "daily_appointments.csv")
    txt_file = os.path.join(processed_dir, "insurance_complaints.txt")

    # 1. Directory and File Presence (20 points)
    files_exist = os.path.isdir(processed_dir) and os.path.isfile(csv_file) and os.path.isfile(txt_file)
    if files_exist:
        score_details.append({"item": "Check directory and files existence", "score": 20, "max_score": 20, "passed": True, "reason": "All required files exist."})
        total_score += 20
    else:
        score_details.append({"item": "Check directory and files existence", "score": 0, "max_score": 20, "passed": False, "reason": "Missing 'processed' dir or required files."})
        
    # 2. CSV Structure and Deterministic Filtering (30 points)
    # Expected HR people in chronological order:
    # John Doe (08:15 AM), Alice Jones (09:30 AM), Eve Evans (11:00 AM), Tom Clark (12:15 PM), Bob Brown (02:00 PM), Gregory House (04:30 PM)
    expected_names_sorted = ["John Doe", "Alice Jones", "Eve Evans", "Tom Clark", "Bob Brown", "Gregory House"]
    csv_valid = False
    csv_content = ""
    
    if os.path.isfile(csv_file):
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                csv_content = f.read()
                f.seek(0)
                reader = csv.DictReader(f)
                headers = [h.strip().lower() for h in reader.fieldnames or []]
                
                if "time" in headers and "name" in headers and "reason" in headers:
                    rows = list(reader)
                    
                    actual_names = []
                    # Locate case-insensitive keys
                    time_key = next(k for k in reader.fieldnames if k.strip().lower() == 'time')
                    name_key = next(k for k in reader.fieldnames if k.strip().lower() == 'name')
                    
                    for row in rows:
                        actual_names.append(row[name_key].strip())
                        
                    if actual_names == expected_names_sorted:
                        score_details.append({"item": "CSV Filtering and Chronological Sorting", "score": 30, "max_score": 30, "passed": True, "reason": "Accurately filtered HR individuals and sorted them chronologically."})
                        total_score += 30
                        csv_valid = True
                    else:
                        score_details.append({"item": "CSV Filtering and Chronological Sorting", "score": 10, "max_score": 30, "passed": False, "reason": f"Names/Sorting mismatch. Expected {expected_names_sorted}, got {actual_names}"})
                        total_score += 10
                else:
                    score_details.append({"item": "CSV Filtering and Chronological Sorting", "score": 0, "max_score": 30, "passed": False, "reason": "CSV missing required columns (Time, Name, Reason)."})
        except Exception as e:
            score_details.append({"item": "CSV Filtering and Chronological Sorting", "score": 0, "max_score": 30, "passed": False, "reason": f"Failed to parse CSV: {e}"})
    else:
        score_details.append({"item": "CSV Filtering and Chronological Sorting", "score": 0, "max_score": 30, "passed": False, "reason": "CSV file missing."})

    # 3. Deterministic txt Extraction Check (20 points)
    txt_content = ""
    if os.path.isfile(txt_file):
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                txt_content = f.read()
            
            has_alice = "Alice Jones" in txt_content
            has_eve = "Eve Evans" in txt_content
            has_others = any(name in txt_content for name in ["John Doe", "Jane Smith", "Bob Brown", "Charlie Davis", "Gregory House", "Sarah Connor", "Tom Clark"])
            
            if has_alice and has_eve and not has_others:
                score_details.append({"item": "Insurance Complaints Extraction", "score": 20, "max_score": 20, "passed": True, "reason": "Correctly isolated Alice and Eve without other individuals."})
                total_score += 20
            else:
                score_details.append({"item": "Insurance Complaints Extraction", "score": 5, "max_score": 20, "passed": False, "reason": "Text file contains incorrect individuals or misses the targets."})
                total_score += 5
        except Exception as e:
             score_details.append({"item": "Insurance Complaints Extraction", "score": 0, "max_score": 20, "passed": False, "reason": f"Error reading text file: {e}"})
    else:
        score_details.append({"item": "Insurance Complaints Extraction", "score": 0, "max_score": 20, "passed": False, "reason": "Text file missing."})

    # 4. LLM Semantic Verification for Summaries (30 points)
    if csv_valid and txt_content:
        prompt = (
            "Evaluate the provided CSV and Text file contents. "
            "1. Does the CSV correctly describe HR-related tasks (like interviews, payroll, applications, direct deposit)? "
            "2. Does the Text file accurately describe 'health insurance' complaints/disputes for the individuals listed? "
            "Respond 'YES' only if both conditions are met."
        )
        combined_content = f"--- CSV Content ---\n{csv_content}\n\n--- TXT Content ---\n{txt_content}"
        llm_passed = llm_judge_content(prompt, combined_content)
        
        if llm_passed:
            score_details.append({"item": "Semantic validation of generated reasons", "score": 30, "max_score": 30, "passed": True, "reason": "LLM confirmed reasons are semantically correct."})
            total_score += 30
        else:
            score_details.append({"item": "Semantic validation of generated reasons", "score": 0, "max_score": 30, "passed": False, "reason": "LLM detected hallucinated or incorrect summaries."})
    else:
        score_details.append({"item": "Semantic validation of generated reasons", "score": 0, "max_score": 30, "passed": False, "reason": "Prerequisite files invalid or missing."})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2)

if __name__ == "__main__":
    main()
