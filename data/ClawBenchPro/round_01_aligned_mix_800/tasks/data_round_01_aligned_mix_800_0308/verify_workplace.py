import os
import sys
import json
import csv
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

def extract_all_strings_from_json(data):
    """Recursively extract all string values from a JSON object/array."""
    strings = set()
    if isinstance(data, dict):
        for k, v in data.items():
            strings.add(str(k))
            strings.update(extract_all_strings_from_json(v))
    elif isinstance(data, list):
        for item in data:
            strings.update(extract_all_strings_from_json(item))
    elif isinstance(data, str):
        strings.add(data)
    elif data is not None:
        strings.add(str(data))
    return strings

def parse_and_extract_ids(file_path):
    """Attempt to parse file as JSON, then CSV, extracting all text values."""
    extracted = set()
    is_valid_format = False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            data = json.loads(content)
            extracted = extract_all_strings_from_json(data)
            is_valid_format = True
        except json.JSONDecodeError:
            try:
                # Try parsing as CSV
                f.seek(0)
                reader = csv.reader(f)
                for row in reader:
                    for cell in row:
                        extracted.add(cell.strip())
                if len(extracted) > 0:
                    is_valid_format = True
            except Exception:
                pass
    except Exception:
        pass
        
    return extracted, is_valid_format

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # Check 1: Directory exists (15 points)
    if os.path.isdir(deliverables_dir):
        score_details.append({"item": "Deliverables directory creation", "score": 15, "max_score": 15, "passed": True, "reason": "Directory 'deliverables' exists."})
        total_score += 15
    else:
        score_details.append({"item": "Deliverables directory creation", "score": 0, "max_score": 15, "passed": False, "reason": "Directory 'deliverables' is missing."})
        
    # Find files in deliverables
    files_found = []
    if os.path.isdir(deliverables_dir):
        files_found = [os.path.join(deliverables_dir, f) for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]

    target_file = files_found[0] if len(files_found) == 1 else None
    
    # Check 2: Single file generated and properly structured (15 points)
    is_valid_format = False
    extracted_ids = set()
    file_content = ""
    
    if len(files_found) == 1:
        target_file = files_found[0]
        with open(target_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        extracted_ids, is_valid_format = parse_and_extract_ids(target_file)
        
        if is_valid_format:
            score_details.append({"item": "Structured data generation", "score": 15, "max_score": 15, "passed": True, "reason": "Single structured file (JSON/CSV) generated successfully."})
            total_score += 15
        else:
            score_details.append({"item": "Structured data generation", "score": 0, "max_score": 15, "passed": False, "reason": "File exists but is not valid JSON or CSV."})
    else:
        score_details.append({"item": "Structured data generation", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected exactly 1 file in deliverables, found {len(files_found)}."})
    
    # Check 3: Data correctness - Invalid claims presence (50 points, 10 per claim correctly classified)
    # Ground Truth: 
    # Invalid (Must be in file): CLM-8811, CLM-8812, CLM-8813
    # Valid (Must NOT be in file): CLM-8810, CLM-8814
    
    claim_checks = [
        {"id": "CLM-8811", "should_exist": True, "reason_msg": "Invalid claim (Exceeds limit) correctly included."},
        {"id": "CLM-8812", "should_exist": True, "reason_msg": "Invalid claim (Predates policy) correctly included."},
        {"id": "CLM-8813", "should_exist": True, "reason_msg": "Invalid claim (Slightly exceeds limit) correctly included."},
        {"id": "CLM-8810", "should_exist": False, "reason_msg": "Valid claim correctly excluded."},
        {"id": "CLM-8814", "should_exist": False, "reason_msg": "Valid claim correctly excluded."}
    ]
    
    data_score = 0
    if is_valid_format:
        for check in claim_checks:
            exists = any(check["id"] in val for val in extracted_ids)
            if exists == check["should_exist"]:
                data_score += 10
                score_details.append({"item": f"Classification of {check['id']}", "score": 10, "max_score": 10, "passed": True, "reason": check["reason_msg"]})
            else:
                score_details.append({"item": f"Classification of {check['id']}", "score": 0, "max_score": 10, "passed": False, "reason": f"Incorrectly {'included' if exists else 'excluded'}."})
        total_score += data_score
    else:
        score_details.append({"item": "Accurate Data Cross-Referencing", "score": 0, "max_score": 50, "passed": False, "reason": "Cannot verify data correctness due to invalid file format or missing file."})
        
    # Check 4: LLM check for clean machine-readability (20 points)
    if is_valid_format and file_content:
        prompt = (
            "Analyze the following file content. The user requested a 'pristine, perfectly organized report "
            "containing ONLY the invalid claims... in a clean, structured machine-readable format'. "
            "Does the file contain purely structured data (like JSON or CSV) WITHOUT any conversational text, "
            "apologies, markdown chat wrappers, or hallucinated/fake fields? Answer 'YES' if it is strictly clean data, 'NO' otherwise."
        )
        is_clean = llm_judge_content(prompt, file_content)
        if is_clean:
            score_details.append({"item": "Cleanliness and Formatting (LLM)", "score": 20, "max_score": 20, "passed": True, "reason": "No conversational bloat detected."})
            total_score += 20
        else:
            score_details.append({"item": "Cleanliness and Formatting (LLM)", "score": 0, "max_score": 20, "passed": False, "reason": "File contains conversational padding, markdown wrappers, or hallucinated fields."})
    else:
        score_details.append({"item": "Cleanliness and Formatting (LLM)", "score": 0, "max_score": 20, "passed": False, "reason": "Skip check: Missing or invalid file."})

    # Save Results
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2)
        
    print(f"Workplace Verification Completed. Total Score: {total_score}/100")

if __name__ == "__main__":
    main()
