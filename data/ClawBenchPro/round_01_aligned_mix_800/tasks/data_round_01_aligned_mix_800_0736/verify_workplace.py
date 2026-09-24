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
    score_details = []
    total_score = 0

    # Expected Values (Calculated from env_builder)
    # ThreeSistersStew: 
    # Cost: (1.5*0.5)+(2.0*0.3)+(1.0*0.8) = 0.75 + 0.6 + 0.8 = 2.15
    # Cals: (1.5*50)+(2.0*80)+(1.0*40) = 75 + 160 + 40 = 275
    # BisonSliders:
    # Cost: (2.0*3.0)+(1.0*0.5)+(0.5*0.2) = 6.0 + 0.5 + 0.1 = 6.6
    # Cals: (2.0*200)+(1.0*150)+(0.5*50) = 400 + 150 + 25 = 575

    expected_results = {
        "ThreeSistersStew": {"cost": 2.15, "calories": 275},
        "BisonSliders": {"cost": 6.6, "calories": 575}
    }

    # 1. Structure Check (10 points)
    pres_dir = os.path.join(workspace, "presentation")
    if os.path.isdir(pres_dir):
        score_details.append({"item": "Directory presentation exists", "score": 10, "max_score": 10, "passed": True, "reason": "Folder created correctly."})
        total_score += 10
    else:
        score_details.append({"item": "Directory presentation exists", "score": 0, "max_score": 10, "passed": False, "reason": "Folder 'presentation' not found."})

    # 2. File Content Check (90 points)
    # Finding the report file (any text/md file in presentation)
    report_file = None
    if os.path.isdir(pres_dir):
        files = [f for f in os.listdir(pres_dir) if f.endswith(('.txt', '.md', '.pdf'))]
        if files:
            report_file = os.path.join(pres_dir, files[0])

    if not report_file:
        score_details.append({"item": "Report file exists", "score": 0, "max_score": 90, "passed": False, "reason": "No report file found in presentation directory."})
    else:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Numeric Accuracy Check (60 points - 15 per value)
        for meal, data in expected_results.items():
            cost_str = f"{data['cost']:.2f}"
            cal_str = str(data['calories'])
            
            # Check Cost
            if cost_str in content or str(data['cost']) in content:
                score_details.append({"item": f"Accuracy: {meal} Cost", "score": 15, "max_score": 15, "passed": True, "reason": f"Correct cost {cost_str} found."})
                total_score += 15
            else:
                score_details.append({"item": f"Accuracy: {meal} Cost", "score": 0, "max_score": 15, "passed": False, "reason": f"Cost {cost_str} not found for {meal}."})
            
            # Check Calories
            if cal_str in content:
                score_details.append({"item": f"Accuracy: {meal} Calories", "score": 15, "max_score": 15, "passed": True, "reason": f"Correct calories {cal_str} found."})
                total_score += 15
            else:
                score_details.append({"item": f"Accuracy: {meal} Calories", "score": 0, "max_score": 15, "passed": False, "reason": f"Calories {cal_str} not found for {meal}."})

        # Tone and Professionalism (LLM Judge) (30 points)
        prompt = "Does this report look like a formal, clean summary report suitable for a school board meeting? Is it professional and does it explicitly mention ThreeSistersStew and BisonSliders while ignoring the discarded Veggie Bake?"
        if llm_judge_content(prompt, content):
            score_details.append({"item": "Formal Summary Quality", "score": 30, "max_score": 30, "passed": True, "reason": "LLM confirmed the report is professional and focused."})
            total_score += 30
        else:
            score_details.append({"item": "Formal Summary Quality", "score": 0, "max_score": 30, "passed": False, "reason": "LLM judged the report as unprofessional or missing required context/filtering."})

    # Final Output
    result = {
        "total_score": int(total_score),
        "details": score_details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
