import os
import sys
import json
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
    """Unified interface for non-structured text validation."""
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
    
    report_path = os.path.join(workspace, "report/conflict_summary.json")
    
    # 1. Check file existence (10 points)
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "Check report existence", "score": 10, "max_score": 10, "passed": True, "reason": "File exists."})
    else:
        details.append({"item": "Check report existence", "score": 0, "max_score": 10, "passed": False, "reason": "File not found."})
        # Cannot proceed without file
        final_output(score, details)
        return

    # 2. Check JSON validity (10 points)
    data = {}
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "JSON Format Validation", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON format."})
    except Exception as e:
        details.append({"item": "JSON Format Validation", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        final_output(score, details)
        return

    # 3. Check for the exactly three pieces of information constraint (10 points)
    # The prompt asks for "exactly three pieces of information"
    if len(data.keys()) == 3:
        score += 10
        details.append({"item": "Constraint: Exactly 3 fields", "score": 10, "max_score": 10, "passed": True, "reason": "Report contains exactly three keys."})
    else:
        details.append({"item": "Constraint: Exactly 3 fields", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 3 fields, found {len(data.keys())}."})

    # 4. Verify Library Name (25 points)
    # Use LLM to ensure flexible naming (fmt vs fmtlib)
    lib_name = str(next(iter(data.values()))) # Get first value as a placeholder if keys aren't named
    # Better to look for specific key logic, but prompt didn't define keys. Let's find the library name in the values.
    values_str = json.dumps(data)
    lib_correct = llm_judge_content("Does the following JSON content identify 'fmt' or 'fmtlib' as the conflicting library?", values_str)
    if lib_correct:
        score += 25
        details.append({"item": "Library Identification", "score": 25, "max_score": 25, "passed": True, "reason": "Identified 'fmtlib' correctly."})
    else:
        details.append({"item": "Library Identification", "score": 0, "max_score": 25, "passed": False, "reason": "Failed to identify 'fmtlib' as the conflicting library."})

    # 5. Verify Expected Version (20 points)
    # Expected version in manifest is 9.1.0
    if "9.1.0" in values_str:
        score += 20
        details.append({"item": "Expected Version Accuracy", "score": 20, "max_score": 20, "passed": True, "reason": "Found expected version 9.1.0."})
    else:
        details.append({"item": "Expected Version Accuracy", "score": 0, "max_score": 20, "passed": False, "reason": "Missing or incorrect expected version (should be 9.1.0)."})

    # 6. Verify Rogue Version (25 points)
    # Rogue version in log is 8.0.1
    if "8.0.1" in values_str:
        score += 25
        details.append({"item": "Rogue Version Accuracy", "score": 25, "max_score": 25, "passed": True, "reason": "Found rogue version 8.0.1."})
    else:
        details.append({"item": "Rogue Version Accuracy", "score": 0, "max_score": 25, "passed": False, "reason": "Missing or incorrect rogue version (should be 8.0.1)."})

    final_output(score, details)

def final_output(score, details):
    output = {
        "total_score": min(100, score),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
