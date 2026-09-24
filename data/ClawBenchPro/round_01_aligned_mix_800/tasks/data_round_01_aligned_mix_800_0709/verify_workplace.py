import os
import sys
import json
import csv
import re
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
    score_details = []
    total_score = 0

    prep_work_dir = os.path.join(workspace, "prep_work")
    
    # 1. Directory Structure (10 points)
    if os.path.exists(prep_work_dir) and os.path.isdir(prep_work_dir):
        score_details.append({"item": "Directory prep_work created", "score": 10, "max_score": 10, "passed": True, "reason": "Found prep_work directory."})
        total_score += 10
    else:
        score_details.append({"item": "Directory prep_work created", "score": 0, "max_score": 10, "passed": False, "reason": "Directory prep_work not found."})

    # 2. Summary Document Existence (10 points)
    # Find any document in the prep_work folder (usually summary.txt or similar)
    summary_files = [f for f in os.listdir(prep_work_dir) if os.path.isfile(os.path.join(prep_work_dir, f))] if os.path.exists(prep_work_dir) else []
    summary_path = None
    if summary_files:
        summary_path = os.path.join(prep_work_dir, summary_files[0])
        score_details.append({"item": "Summary document exists", "score": 10, "max_score": 10, "passed": True, "reason": f"Found {summary_files[0]}"})
        total_score += 10
    else:
        score_details.append({"item": "Summary document exists", "score": 0, "max_score": 10, "passed": False, "reason": "No file found in prep_work."})

    # Read content for further verification
    content = ""
    if summary_path:
        with open(summary_path, 'r', encoding='utf-8') as f:
            content = f.read()

    # 3. Calculation Check: Danny's Tip Cut (30 points)
    # Expected: 100*0.2 + 250*0.2 + 50*0.2 + 1500*0.18 = 20 + 50 + 10 + 270 = 350.00
    if "350" in content:
        score_details.append({"item": "Tip calculation accuracy", "score": 30, "max_score": 30, "passed": True, "reason": "Correct tip total ($350.00) identified."})
        total_score += 30
    else:
        score_details.append({"item": "Tip calculation accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "Incorrect tip total or value not found."})

    # 4. Inventory Logic: Cocktail Selection (30 points)
    # Irish Sunrise: Needs Grenadine (OUT)
    # Missouri Mule: Needs Vodka, Ginger Beer, Lime (All IN) -> WINNER
    # Midwest Fidget: Needs Bourbon (OUT)
    # Winning cocktail: Missouri Mule
    if "Missouri Mule" in content and "Irish Sunrise" not in content.split("winning")[0] and "Midwest Fidget" not in content.split("winning")[0]:
        # Simple string check for the winner, but refined by logic
        if "Irish Sunrise" not in content and "Midwest Fidget" not in content:
            score_details.append({"item": "Cocktail filtering logic", "score": 30, "max_score": 30, "passed": True, "reason": "Correctly identified Missouri Mule as the only available option."})
            total_score += 30
        else:
            score_details.append({"item": "Cocktail filtering logic", "score": 15, "max_score": 30, "passed": False, "reason": "Identified Missouri Mule but failed to exclude out-of-stock drinks."})
            total_score += 15
    else:
        score_details.append({"item": "Cocktail filtering logic", "score": 0, "max_score": 30, "passed": False, "reason": "Did not identify the correct winning cocktail."})

    # 5. Professionalism & Formatting (20 points)
    if content:
        prompt = "Does this document look like a neat, professional summary for a boss? It should clearly list 'winning cocktails' and a 'tip total' without showing messy raw code or debug logs."
        if llm_judge_content(prompt, content):
            score_details.append({"item": "Professional formatting", "score": 20, "max_score": 20, "passed": True, "reason": "LLM judged the document as professional."})
            total_score += 20
        else:
            score_details.append({"item": "Professional formatting", "score": 5, "max_score": 20, "passed": False, "reason": "Document content is messy or lacks professional structure."})
            total_score += 5
    else:
        score_details.append({"item": "Professional formatting", "score": 0, "max_score": 20, "passed": False, "reason": "No content to evaluate."})

    # Final Output
    output = {
        "total_score": int(total_score),
        "details": score_details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    verify()
