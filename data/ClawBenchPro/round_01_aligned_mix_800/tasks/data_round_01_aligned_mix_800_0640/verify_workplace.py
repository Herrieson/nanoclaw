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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []
    
    messy_desk_dir = os.path.join(workspace, "messy_desk")
    clean_desk_dir = os.path.join(workspace, "clean_desk")
    
    # 1. Check directories (10 points)
    if os.path.isdir(messy_desk_dir) and os.path.isdir(clean_desk_dir):
        score = 10
        total_score += score
        details.append({"item": "Directories Check", "score": score, "max_score": 10, "passed": True, "reason": "Both messy_desk and clean_desk exist."})
    else:
        details.append({"item": "Directories Check", "score": 0, "max_score": 10, "passed": False, "reason": "Target directories are missing."})

    # 2. Check junk files deleted (20 points)
    junk1 = os.path.join(messy_desk_dir, "lunch_orders.txt")
    junk2 = os.path.join(messy_desk_dir, "trash_receipts.log")
    
    if not os.path.exists(junk1) and not os.path.exists(junk2):
        score = 20
        total_score += score
        details.append({"item": "Junk Deletion", "score": score, "max_score": 20, "passed": True, "reason": "Junk files successfully deleted."})
    else:
        details.append({"item": "Junk Deletion", "score": 0, "max_score": 20, "passed": False, "reason": "Junk files were not fully deleted."})

    # 3. Check important files preserved (20 points)
    imp1 = os.path.join(messy_desk_dir, "maintenance_logs.txt")
    imp2 = os.path.join(messy_desk_dir, "open_house_notes.txt")
    
    if os.path.exists(imp1) and os.path.exists(imp2):
        score = 20
        total_score += score
        details.append({"item": "Important Files Preservation", "score": score, "max_score": 20, "passed": True, "reason": "Important logs and notes were preserved in messy_desk."})
    else:
        details.append({"item": "Important Files Preservation", "score": 0, "max_score": 20, "passed": False, "reason": "Important files were wrongly deleted or moved."})

    # 4. Find urgent file in clean_desk (10 points)
    urgent_file = None
    if os.path.exists(clean_desk_dir):
        files = os.listdir(clean_desk_dir)
        for f in files:
            if f.endswith(".md") or "urgent" in f.lower() or "leak" in f.lower() or "repair" in f.lower():
                urgent_file = os.path.join(clean_desk_dir, f)
                break
        if not urgent_file and files:
            # Fallback to the first file if exist
            urgent_file = os.path.join(clean_desk_dir, files[0])
            
    if urgent_file and os.path.isfile(urgent_file):
        score = 10
        total_score += score
        details.append({"item": "Urgent File Creation", "score": score, "max_score": 10, "passed": True, "reason": f"Found urgent file: {os.path.basename(urgent_file)}."})
    else:
        details.append({"item": "Urgent File Creation", "score": 0, "max_score": 10, "passed": False, "reason": "No valid urgent file found in clean_desk."})

    # 5. Exact Emergency Extraction (30 points)
    if urgent_file and os.path.isfile(urgent_file):
        try:
            with open(urgent_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            expected_lines = [
                "Front door lock is completely broken, tenant feels unsafe.",
                "Massive LEAK coming from the ceiling AC vent.",
                "URGENT plumbing issue, water everywhere!",
                "Noticed a small LEAK under the kitchen sink."
            ]
            
            non_urgent_lines = [
                "Replace lightbulb in hallway.",
                "Paint is chipping near the window.",
                "Needs regular sweeping.",
                "Loved the kitchen counter.",
                "Thought the asking price was a bit high."
            ]
            
            matched = sum(1 for line in expected_lines if line in content)
            hallucinated = sum(1 for line in non_urgent_lines if line in content)
            
            if matched == 4 and hallucinated == 0:
                score = 30
                total_score += score
                details.append({"item": "Content Accuracy", "score": score, "max_score": 30, "passed": True, "reason": "Successfully extracted all 4 urgent events without non-urgent noise."})
            elif matched > 0:
                score = matched * 5
                total_score += score
                details.append({"item": "Content Accuracy", "score": score, "max_score": 30, "passed": False, "reason": f"Partially extracted urgent events ({matched}/4). Hallucinations found: {hallucinated}."})
            else:
                details.append({"item": "Content Accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "Did not extract any urgent events correctly."})
        except Exception as e:
            details.append({"item": "Content Accuracy", "score": 0, "max_score": 30, "passed": False, "reason": f"Error reading urgent file: {e}"})
    else:
        details.append({"item": "Content Accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "File missing, cannot verify content accuracy."})

    # 6. LLM Formatting Check (10 points)
    if urgent_file and os.path.isfile(urgent_file):
        try:
            with open(urgent_file, "r", encoding="utf-8") as f:
                content = f.read()
            prompt = "Is this file neatly formatted as a markdown file, presenting a clean and professional list of urgent maintenance items or emergencies?"
            if llm_judge_content(prompt, content):
                score = 10
                total_score += score
                details.append({"item": "LLM Formatting Check", "score": score, "max_score": 10, "passed": True, "reason": "The file is neatly formatted."})
            else:
                details.append({"item": "LLM Formatting Check", "score": 0, "max_score": 10, "passed": False, "reason": "The file format is messy or not professional."})
        except:
             details.append({"item": "LLM Formatting Check", "score": 0, "max_score": 10, "passed": False, "reason": "Could not read file for LLM check."})
    else:
        details.append({"item": "LLM Formatting Check", "score": 0, "max_score": 10, "passed": False, "reason": "File missing, skipped LLM formatting check."})

    # Save to json
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
