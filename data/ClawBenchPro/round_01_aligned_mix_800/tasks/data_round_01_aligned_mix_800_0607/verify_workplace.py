import os
import sys
import json
import httpx
from openai import OpenAI

# Configuration for LLM
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize client
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
    score_details = []
    total_score = 0

    # 1. Check deliverables directory (10 pts)
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        score_details.append({"item": "Directory existence (deliverables/)", "score": 10, "max_score": 10, "passed": True, "reason": "Found deliverables directory."})
        total_score += 10
    else:
        score_details.append({"item": "Directory existence (deliverables/)", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables/ directory not found."})

    # 2. Check summary file existence (10 pts)
    # The prompt asked for a document, let's look for common formats (JSON/TXT/MD)
    summary_file = None
    for f in os.listdir(deliverables_dir) if os.path.exists(deliverables_dir) else []:
        if "summary" in f.lower():
            summary_file = os.path.join(deliverables_dir, f)
            break
    
    if summary_file:
        score_details.append({"item": "Executive summary file existence", "score": 10, "max_score": 10, "passed": True, "reason": f"Found summary file: {os.path.basename(summary_file)}"})
        total_score += 10
    else:
        score_details.append({"item": "Executive summary file existence", "score": 0, "max_score": 10, "passed": False, "reason": "No summary file found in deliverables/."})

    # 3. Structural & Calculation Check (Data Verification)
    # Target Values:
    # Authorized Cost Calculation:
    # - TechNova: (40h from CSV + 10h from JSON) * 150 = 7500
    # - ByteSynergy: 15h * 200 = 3000
    # - CloudArchitects: 20h * 180 = 3600
    # Total Authorized: 14100
    # Unauthorized Vendors: RogueIT Contractors, ShadowCoders
    
    if summary_file:
        content = ""
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for Unauthorized Vendors (30 pts)
        # We look for RogueIT and ShadowCoders. 15 pts each.
        rogue_ok = "rogueit" in content.lower().replace(" ", "")
        shadow_ok = "shadowcoders" in content.lower().replace(" ", "")
        
        rogue_score = 15 if rogue_ok else 0
        shadow_score = 15 if shadow_ok else 0
        total_score += (rogue_score + shadow_score)
        score_details.append({"item": "Detection of RogueIT Contractors", "score": rogue_score, "max_score": 15, "passed": rogue_ok, "reason": "Found in summary" if rogue_ok else "Missing"})
        score_details.append({"item": "Detection of ShadowCoders", "score": shadow_score, "max_score": 15, "passed": shadow_ok, "reason": "Found in summary" if shadow_ok else "Missing"})

        # Check for Calculation Result (40 pts)
        # Total should be 14100.
        # Strict numerical check via LLM or regex? Let's use LLM to handle "total cost: $14,100" etc.
        calc_prompt = "Does this summary explicitly state that the total cost for authorized vendors is exactly 14100 (ignore currency symbols and commas)?"
        calc_passed = llm_judge_content(calc_prompt, content)
        
        calc_score = 40 if calc_passed else 0
        total_score += calc_score
        score_details.append({"item": "Calculation of total authorized cost ($14,100)", "score": calc_score, "max_score": 40, "passed": calc_passed, "reason": "Correct total cost identified" if calc_passed else "Incorrect or missing total cost"})

        # Check Executive Tone & PM Appropriateness (10 pts)
        tone_prompt = "Is this document formatted as an executive summary suitable for a PM to present to a steering committee? It should be professional and focused on the two required metrics."
        tone_passed = llm_judge_content(tone_prompt, content)
        tone_score = 10 if tone_passed else 0
        total_score += tone_score
        score_details.append({"item": "Executive summary tone and structure", "score": tone_score, "max_score": 10, "passed": tone_passed, "reason": "Professional executive summary" if tone_passed else "Tone or format unsuitable"})

    # Output results
    output = {
        "total_score": int(total_score),
        "details": score_details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    verify()
