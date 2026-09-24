import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize client with SSL verification disabled
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """Unified interface for LLM non-structured semantic validation."""
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    admin_dir = os.path.join(workspace, "admin_delivery")
    
    # Item 1: Directory Existence (10 points)
    if os.path.exists(admin_dir) and os.path.isdir(admin_dir):
        score_details.append({
            "item": "Directory 'admin_delivery' exists",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "Directory exists."
        })
        total_score += 10
    else:
        score_details.append({
            "item": "Directory 'admin_delivery' exists",
            "score": 0, "max_score": 10, "passed": False,
            "reason": "Directory not found."
        })
        
    # Item 2: Report file exists and readable (10 points)
    report_content = ""
    if os.path.exists(admin_dir) and os.path.isdir(admin_dir):
        files = os.listdir(admin_dir)
        for f in files:
            f_path = os.path.join(admin_dir, f)
            if os.path.isfile(f_path):
                try:
                    with open(f_path, "r", encoding="utf-8") as file:
                        report_content += file.read() + "\n"
                except Exception:
                    pass
        if report_content.strip():
            score_details.append({
                "item": "Report file exists and is readable",
                "score": 10, "max_score": 10, "passed": True,
                "reason": "Successfully read report file(s)."
            })
            total_score += 10
        else:
            score_details.append({
                "item": "Report file exists and is readable",
                "score": 0, "max_score": 10, "passed": False,
                "reason": "Files present but empty or unreadable text."
            })
    else:
        score_details.append({
            "item": "Report file exists and is readable",
            "score": 0, "max_score": 10, "passed": False,
            "reason": "Directory not found."
        })
        
    # Cascading failures if no content
    if not report_content.strip():
        score_details.append({"item": "Extracts correct Charity patients", "score": 0, "max_score": 30, "passed": False, "reason": "No readable content."})
        score_details.append({"item": "Calculates and includes total 11.0 hours", "score": 0, "max_score": 20, "passed": False, "reason": "No readable content."})
        score_details.append({"item": "Professional tone and formatting", "score": 0, "max_score": 30, "passed": False, "reason": "No readable content."})
    else:
        # Item 3: Patient IDs Verification via exact string matching (Code Level, 30 points)
        expected_patients = ["P-002", "P-003", "P-004", "P-006"]
        unexpected_patients = ["P-001", "P-005", "P-007"]
        content_upper = report_content.upper()
        
        found_expected = [p for p in expected_patients if p in content_upper]
        found_unexpected = [p for p in unexpected_patients if p in content_upper]
        
        patient_score = len(found_expected) * 5
        if len(found_expected) == 4:
            patient_score += 10  # Bonus for finding all correct patients
            
        patient_score -= len(found_unexpected) * 10 # Strict penalty for hallucinated/wrong patients
        patient_score = max(0, min(30, patient_score))
        
        passed_patients = (patient_score == 30)
        reason_pts = f"Found expected: {found_expected}. Found unexpected (hallucinations): {found_unexpected}."
        score_details.append({
            "item": "Extracts correct Charity patients",
            "score": patient_score, "max_score": 30, "passed": passed_patients,
            "reason": reason_pts
        })
        total_score += patient_score
        
        # Item 4: Total Hours Verification (LLM Level, 20 points)
        llm_time_prompt = (
            "Check if the provided report explicitly states that the grand total of hours (or duration) "
            "spent with 'Charity' patients is exactly 11 or 11.0 (eleven). Answer ONLY 'YES' or 'NO'."
        )
        time_passed = llm_judge_content(llm_time_prompt, report_content)
        t_score = 20 if time_passed else 0
        score_details.append({
            "item": "Calculates and includes total 11.0 hours",
            "score": t_score, "max_score": 20, "passed": time_passed,
            "reason": "LLM verified the grand total is exactly 11 or 11.0." if time_passed else "LLM did not find explicit mention of correct 11/11.0 hours."
        })
        total_score += t_score
        
        # Item 5: Professional Tone (LLM Level, 30 points)
        llm_prof_prompt = (
            "Check if the report is written in a clean, professional tone suitable for a hospital administration team. "
            "It should NOT include the doctor's neurotic, anxious, or informal rambling from the prompt. "
            "It MUST present the patient and hours data clearly. Answer ONLY 'YES' or 'NO'."
        )
        prof_passed = llm_judge_content(llm_prof_prompt, report_content)
        p_score = 30 if prof_passed else 0
        score_details.append({
            "item": "Professional tone and formatting",
            "score": p_score, "max_score": 30, "passed": prof_passed,
            "reason": "LLM verified clean, professional tone." if prof_passed else "LLM flagged the tone as unprofessional, rambling, or poorly formatted."
        })
        total_score += p_score

    # Save validation results
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=4)

if __name__ == "__main__":
    main()
