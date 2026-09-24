import os
import sys
import json
import csv
import re
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

def calculate_ground_truth_tip(workspace):
    """通过代码在本地重算Ground Truth，应对随机种子可能的细微扰动"""
    total_tip = 0.0
    pos_dir = os.path.join(workspace, "pos_data", "yesterday_10_26")
    if not os.path.exists(pos_dir):
        return None
    
    for filename in os.listdir(pos_dir):
        if not filename.endswith(".csv"):
            continue
        filepath = os.path.join(pos_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Status") == "VOID":
                    continue
                if row.get("Helper_ID") != "EMP-8492": # Danny's ID
                    continue
                
                tip_amount = float(row.get("Tip_Amount", 0))
                party_size = int(row.get("Party_Size", 0))
                server = row.get("Server_Name", "")

                # Rule Precedence: Party >= 8 overrides Server == Sarah
                if party_size >= 8:
                    cut_ratio = 0.15
                elif server == "Sarah":
                    cut_ratio = 0.25
                else:
                    cut_ratio = 0.20
                
                total_tip += tip_amount * cut_ratio
                
    return round(total_tip, 2)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 1. Check Directory & File Existence (10 points)
    prep_dir = os.path.join(workspace, "prep_work")
    summary_file = os.path.join(prep_dir, "summary.txt")
    
    if os.path.isdir(prep_dir) and os.path.isfile(summary_file):
        score = 10
        passed = True
        reason = "Output directory 'prep_work' and 'summary.txt' exist."
    else:
        score = 0
        passed = False
        reason = "Missing 'prep_work/summary.txt'. Agent failed basic file creation."
    
    total_score += score
    results.append({"item": "检查目标目录和文件是否存在", "score": score, "max_score": 10, "passed": passed, "reason": reason})

    if not passed:
        # 提前终止，写入0分结果
        write_score(total_score, results)
        return

    with open(summary_file, 'r', encoding='utf-8') as f:
        content = f.read()
    content_lower = content.lower()

    # 2. Check Accurate Tip Calculation (40 points)
    gt_tip = calculate_ground_truth_tip(workspace)
    if gt_tip is None:
        results.append({"item": "校验Tip计算结果", "score": 0, "max_score": 40, "passed": False, "reason": "System Error: POS Data not found in workspace."})
    else:
        # Extract all potential float numbers from the text
        numbers_in_text = re.findall(r'\d+\.\d+', content)
        found_correct_tip = any(abs(float(num) - gt_tip) < 0.05 for num in numbers_in_text)
        
        if found_correct_tip:
            score = 40
            passed = True
            reason = f"Tip calculation matches ground truth strictly ({gt_tip})."
        else:
            score = 0
            passed = False
            reason = f"Failed to find the strictly correct tip amount ({gt_tip}) in the document. Found numbers: {numbers_in_text}"
        
        total_score += score
        results.append({"item": "严格校验Tip多步计算精准度", "score": score, "max_score": 40, "passed": passed, "reason": reason})

    # 3. Check Cocktail Selection Logic (30 points)
    # The only valid cocktail is Missouri Mule.
    has_mule = "missouri mule" in content_lower
    has_sunrise = "irish sunrise" in content_lower
    has_fidget = "midwest fidget" in content_lower
    
    if has_mule and not has_sunrise and not has_fidget:
        score = 30
        passed = True
        reason = "Correctly identified 'Missouri Mule' as the only valid cocktail and eliminated 86'd recipes."
    elif has_mule:
        score = 15
        passed = False
        reason = "Included 'Missouri Mule', but failed to strictly eliminate 'Irish Sunrise' or 'Midwest Fidget' (likely failed to read final stockroom log)."
    else:
        score = 0
        passed = False
        reason = "Did not recommend the correct cocktail 'Missouri Mule'."
    
    total_score += score
    results.append({"item": "检查菜谱筛选及陷阱避让逻辑", "score": score, "max_score": 30, "passed": passed, "reason": reason})

    # 4. LLM Semantic Check for Tone and Completeness (20 points)
    prompt = (
        "Check if the following text is a neat, professional summary document written by a bartender helper named Danny "
        "to the head bartender or management. It should politely present his cocktail pitch and state his calculated tip cut. "
        "If it is well-formatted, polite, and clearly presents both pieces of information, answer YES. Otherwise answer NO."
    )
    is_professional = llm_judge_content(prompt, content)
    
    if is_professional:
        score = 20
        passed = True
        reason = "LLM judged the document tone and format as professional and complete."
    else:
        score = 0
        passed = False
        reason = "LLM judged the document as unprofessional, poorly formatted, or missing required semantic elements."
    
    total_score += score
    results.append({"item": "利用大模型检查文本专业度与语义完整性", "score": score, "max_score": 20, "passed": passed, "reason": reason})

    # Write final result
    write_score(total_score, results)

def write_score(total_score, results):
    output_data = {
        "total_score": total_score,
        "details": results
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(json.dumps(output_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    verify()
