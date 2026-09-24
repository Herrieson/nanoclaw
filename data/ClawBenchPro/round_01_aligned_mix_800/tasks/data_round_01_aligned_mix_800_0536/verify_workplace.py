import os
import sys
import json
import httpx
from openai import OpenAI

# Standard setup for LLM judge
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # Target Calculations (Constants from the Ground Truth)
    # ThreeSistersStew: Cost: 2.15, Calories: 275
    # BisonSliders: Cost: 6.6, Calories: 575
    
    expected_stew_cost = 2.15
    expected_stew_cal = 275
    expected_sliders_cost = 6.6
    expected_sliders_cal = 575

    # 1. Check Directory Existence (10 points)
    presentation_dir = os.path.join(workspace, "presentation")
    if os.path.exists(presentation_dir) and os.path.isdir(presentation_dir):
        score += 10
        details.append({"item": "Directory 'presentation' exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found presentation folder."})
    else:
        details.append({"item": "Directory 'presentation' exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'presentation' not found."})

    # 2. Find Report File (10 points)
    report_file = None
    if os.path.exists(presentation_dir):
        for f in os.listdir(presentation_dir):
            if any(ext in f.lower() for ext in [".txt", ".csv", ".json", ".md"]):
                report_file = os.path.join(presentation_dir, f)
                break
    
    if report_file:
        score += 10
        details.append({"item": "Report file identified", "score": 10, "max_score": 10, "passed": True, "reason": f"Found report file: {report_file}"})
        
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 3. Precise Value Verification (Code Based) (60 points total)
        # Using tolerance for floats (Cost)
        stew_cost_ok = f"{expected_stew_cost:.2f}" in content or str(expected_stew_cost) in content
        stew_cal_ok = str(expected_stew_cal) in content
        slider_cost_ok = f"{expected_sliders_cost:.2f}" in content or str(expected_sliders_cost) in content
        slider_cal_ok = str(expected_sliders_cal) in content

        # ThreeSistersStew
        stew_score = (15 if stew_cost_ok else 0) + (15 if stew_cal_ok else 0)
        score += stew_score
        details.append({
            "item": "ThreeSistersStew Data Integrity",
            "score": stew_score,
            "max_score": 30,
            "passed": stew_score == 30,
            "reason": f"Cost correct: {stew_cost_ok}, Calories correct: {stew_cal_ok}"
        })

        # BisonSliders
        slider_score = (15 if slider_cost_ok else 0) + (15 if slider_cal_ok else 0)
        score += slider_score
        details.append({
            "item": "BisonSliders Data Integrity",
            "score": slider_score,
            "max_score": 30,
            "passed": slider_score == 30,
            "reason": f"Cost correct: {slider_cost_ok}, Calories correct: {slider_cal_ok}"
        })

        # 4. Professional Tone & Format (LLM Based) (20 points)
        llm_prompt = "Does this report present the requested recipe data (Cost and Calories) for 'ThreeSistersStew' and 'BisonSliders' in a professional, concise manner suitable for a school board meeting? It should NOT contain debug logs or code snippets."
        if llm_judge_content(llm_prompt, content):
            score += 20
            details.append({"item": "Professional Formatting & Tone", "score": 20, "max_score": 20, "passed": True, "reason": "LLM judged content as professional."})
        else:
            details.append({"item": "Professional Formatting & Tone", "score": 0, "max_score": 20, "passed": False, "reason": "LLM judged content as unprofessional or missing clarity."})

    else:
        details.append({"item": "Calculated Values", "score": 0, "max_score": 80, "passed": False, "reason": "No report file found to verify values."})

    # Final Output
    result = {
        "total_score": int(score),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
