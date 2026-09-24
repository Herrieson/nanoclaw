import os
import sys
import json
import httpx
import re
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
    
    score_details = []
    total_score = 0
    
    target_dir = os.path.join(workspace, "desk_drawer")
    
    # 1. 检查目标目录是否存在 (15 points)
    if os.path.isdir(target_dir):
        score_details.append({"item": "Check if directory 'desk_drawer' exists", "score": 15, "max_score": 15, "passed": True, "reason": "'desk_drawer' directory exists."})
        total_score += 15
    else:
        score_details.append({"item": "Check if directory 'desk_drawer' exists", "score": 0, "max_score": 15, "passed": False, "reason": "'desk_drawer' directory is missing."})
    
    # 2. 检查是否生成了总结文件 (15 points)
    summary_file = None
    file_content = ""
    if os.path.isdir(target_dir):
        files = os.listdir(target_dir)
        if files:
            summary_file = files[0]
            try:
                with open(os.path.join(target_dir, summary_file), "r", encoding="utf-8") as f:
                    file_content = f.read()
                score_details.append({"item": "Check if summary document is created", "score": 15, "max_score": 15, "passed": True, "reason": f"File '{summary_file}' found and read successfully."})
                total_score += 15
            except Exception as e:
                score_details.append({"item": "Check if summary document is created", "score": 0, "max_score": 15, "passed": False, "reason": f"Failed to read file: {e}"})
        else:
            score_details.append({"item": "Check if summary document is created", "score": 0, "max_score": 15, "passed": False, "reason": "No files found in 'desk_drawer' directory."})
    else:
        score_details.append({"item": "Check if summary document is created", "score": 0, "max_score": 15, "passed": False, "reason": "Target directory is missing."})

    # 3. 检查受损地块是否被正确识别 (30 points)
    if file_content:
        # Expected plots: E1, E2, E3
        found_e1 = bool(re.search(r'\bE1\b', file_content, re.IGNORECASE))
        found_e2 = bool(re.search(r'\bE2\b', file_content, re.IGNORECASE))
        found_e3 = bool(re.search(r'\bE3\b', file_content, re.IGNORECASE))
        
        # Check for false positives (healthy plots or nonexistent ones shouldn't be claimed as compromised)
        # Using negative checks. Only E1, E2, E3 should be mentioned as compromised.
        # But maybe they just listed them. Let's strictly check for E1, E2, E3 presence.
        correct_plots = sum([found_e1, found_e2, found_e3])
        plot_score = correct_plots * 10
        passed = plot_score == 30
        
        # Check if healthy plots are falsely mentioned in the same list context
        false_positives = [p for p in ['W1', 'W2', 'W3', 'N1', 'S1'] if re.search(rf'\b{p}\b', file_content, re.IGNORECASE)]
        
        if false_positives:
            plot_score = max(0, plot_score - len(false_positives) * 5)
            reason = f"Found compromised plots {correct_plots}/3, but contained false positives: {false_positives}. Deducted points."
            passed = False
        else:
            reason = f"Correctly identified {correct_plots}/3 compromised plots."
        
        score_details.append({"item": "Extract and check compromised plots (E1, E2, E3)", "score": plot_score, "max_score": 30, "passed": passed, "reason": reason})
        total_score += plot_score
    else:
        score_details.append({"item": "Extract and check compromised plots (E1, E2, E3)", "score": 0, "max_score": 30, "passed": False, "reason": "No content to check."})

    # 4. 检查计算的准确安全总产量 (20 points)
    if file_content:
        # Expected safe yield is 25500
        found_yield = bool(re.search(r'\b25,?500\b', file_content))
        if found_yield:
            score_details.append({"item": "Check calculated total safe yield", "score": 20, "max_score": 20, "passed": True, "reason": "Accurate total safe yield (25500) found."})
            total_score += 20
        else:
            score_details.append({"item": "Check calculated total safe yield", "score": 0, "max_score": 20, "passed": False, "reason": "Could not find the exact calculated safe yield (25500)."})
    else:
        score_details.append({"item": "Check calculated total safe yield", "score": 0, "max_score": 20, "passed": False, "reason": "No content to check."})

    # 5. LLM 判断：语义与格式检查 (20 points)
    if file_content:
        prompt = (
            "Evaluate if the text provided clearly acts as a summary document containing two specific things: "
            "1) A list or mention of compromised plots. "
            "2) The total projected yield from safe/healthy plots. "
            "It must not be overly wordy or conversational, keeping with a 'brief summary' requested by a busy manager."
        )
        is_good = llm_judge_content(prompt, file_content)
        if is_good:
            score_details.append({"item": "LLM Semantic Check: clear summary layout and tone", "score": 20, "max_score": 20, "passed": True, "reason": "LLM verified the tone and semantic completeness of the summary."})
            total_score += 20
        else:
            score_details.append({"item": "LLM Semantic Check: clear summary layout and tone", "score": 0, "max_score": 20, "passed": False, "reason": "LLM deemed the summary invalid, missing semantics, or too conversational."})
    else:
        score_details.append({"item": "LLM Semantic Check: clear summary layout and tone", "score": 0, "max_score": 20, "passed": False, "reason": "No content to check."})

    # Finalize JSON
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    main()
