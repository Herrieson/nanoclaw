import os
import sys
import json
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    audit_file = os.path.join(deliverables_dir, "audit_summary.json")

    total_score = 0
    details = []

    # 1. Directory Check
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        total_score += 10
        details.append({"item": "Check if deliverables directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory 'deliverables' exists."})
    else:
        details.append({"item": "Check if deliverables directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'deliverables' is missing."})

    # 2. File Check
    if os.path.exists(audit_file) and os.path.isfile(audit_file):
        total_score += 10
        details.append({"item": "Check if audit_summary.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File 'audit_summary.json' exists."})
    else:
        details.append({"item": "Check if audit_summary.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File 'audit_summary.json' is missing."})
        
        # Output early if file is missing
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=4)
        return

    # 3. JSON Validity Check
    try:
        with open(audit_file, "r") as f:
            file_content_str = f.read()
            audit_data = json.loads(file_content_str)
        total_score += 10
        details.append({"item": "Check JSON format validity", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed successfully."})
    except json.JSONDecodeError:
        details.append({"item": "Check JSON format validity", "score": 0, "max_score": 10, "passed": False, "reason": "Invalid JSON format."})
        
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=4)
        return

    # Helper function to flatly search for target strings in JSON values
    def get_all_strings(data):
        strings = []
        if isinstance(data, dict):
            for v in data.values():
                strings.extend(get_all_strings(v))
        elif isinstance(data, list):
            for i in data:
                strings.extend(get_all_strings(i))
        elif isinstance(data, str):
            strings.append(data)
        return strings

    extracted_strings = get_all_strings(audit_data)
    extracted_strings_lower = [s.lower() for s in extracted_strings]

    # 4. Delinquent Payers Check (Max 30)
    # Expected: "Linda Chen", "Robert Taylor"
    # Should NOT have: "James Wilson", "Sarah Miller", "Gina Smith"
    expected_payers = ["linda chen", "robert taylor"]
    not_expected_payers = ["james wilson", "sarah miller", "gina smith"]

    payers_score = 0
    found_expected = [p for p in expected_payers if p in extracted_strings_lower]
    found_unexpected = [p for p in not_expected_payers if p in extracted_strings_lower]

    if len(found_expected) == 2 and len(found_unexpected) == 0:
        payers_score = 30
        msg = "Correctly identified only Linda Chen and Robert Taylor."
    elif len(found_expected) > 0:
        payers_score = 15
        msg = f"Partially correct or included unexpected payers. Found expected: {found_expected}, Unexpected: {found_unexpected}."
    else:
        msg = "Failed to identify the correct delinquent payers."

    total_score += payers_score
    details.append({"item": "Check delinquent payers list accuracy", "score": payers_score, "max_score": 30, "passed": payers_score == 30, "reason": msg})

    # 5. High-Energy Units Check (Max 30)
    # Expected: "A2", "B2", "C1"
    # Should NOT have: "A1", "B1"
    expected_units = ["a2", "b2", "c1"]
    not_expected_units = ["a1", "b1"]

    units_score = 0
    found_expected_units = [u for u in expected_units if u in extracted_strings_lower]
    found_unexpected_units = [u for u in not_expected_units if u in extracted_strings_lower]

    if len(found_expected_units) == 3 and len(found_unexpected_units) == 0:
        units_score = 30
        msg_units = "Correctly identified only A2, B2, and C1 as High-Energy."
    elif len(found_expected_units) > 0:
        units_score = 15
        msg_units = f"Partially correct or included low-energy units. Found expected: {found_expected_units}, Unexpected: {found_unexpected_units}."
    else:
        msg_units = "Failed to identify the high-energy units."

    total_score += units_score
    details.append({"item": "Check high-energy units list accuracy", "score": units_score, "max_score": 30, "passed": units_score == 30, "reason": msg_units})

    # 6. LLM Semantic & Hallucination Check (Max 10)
    # Validate if the JSON structure makes semantic sense and does not contain irrelevant narrative text.
    prompt = "Does this JSON precisely contain ONLY lists or mappings for 'delinquent payers' (names) and 'high-energy units' (unit IDs) without any extra hallucinated commentary, unrelated notes, or polite conversational fillers?"
    
    llm_passed = llm_judge_content(prompt, file_content_str)
    if llm_passed:
        total_score += 10
        details.append({"item": "LLM check for clean, hallucination-free structure", "score": 10, "max_score": 10, "passed": True, "reason": "JSON is clean and contains only requested business logic data."})
    else:
        details.append({"item": "LLM check for clean, hallucination-free structure", "score": 0, "max_score": 10, "passed": False, "reason": "The output contains hallucinated data, conversational filler, or poorly structured keys according to LLM."})

    # Write final score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=4)

if __name__ == "__main__":
    verify()
