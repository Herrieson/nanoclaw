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
    results = []
    total_score = 0
    
    target_dir = os.path.join(workspace, "church_funds")
    target_file = os.path.join(target_dir, "summary.txt")
    
    # 1. Check if the directory and file exist (20 points)
    file_exists = os.path.isfile(target_file)
    if file_exists:
        results.append({
            "item": "检查目标文件 summary.txt 是否存在",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "成功在 church_funds 目录下找到 summary.txt"
        })
        total_score += 20
    else:
        results.append({
            "item": "检查目标文件 summary.txt 是否存在",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "未找到 church_funds/summary.txt 文件"
        })
        
    if not file_exists:
        # End early if the most basic requirement is not met
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)
        return

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        results.append({
            "item": "读取 summary.txt 内容",
            "score": 0,
            "max_score": 80,
            "passed": False,
            "reason": f"读取文件失败: {e}"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)
        return

    # 2. Exact Number Extraction and Calculation Check (50 points)
    # Expected: 
    # Pecan Pie (15.5) + Sweet Tea (5.0) + Brownies (20.0) + Cookies (12.0) + Lemon Pound Cake (18.0) = 70.50
    # Donation (5.0) must be excluded. Gas and personal items excluded.
    
    # Extract all numbers from text
    numbers = re.findall(r'\b\d+\.\d{1,2}\b|\b\d+\b', content.replace(',', ''))
    numbers_float = [float(n) for n in numbers]
    
    calc_score = 0
    calc_reason = "未找到任何与计算结果相关的数字。"
    
    if 70.50 in numbers_float or 70.5 in numbers_float:
        calc_score = 50
        calc_reason = "精确计算出正确的烘焙义卖总收入为 70.50。"
    elif 75.50 in numbers_float or 75.5 in numbers_float:
        calc_score = 20
        calc_reason = "计算错误。包含了不应计入的5美元捐款，得分为20分。"
    elif 52.50 in numbers_float or 52.5 in numbers_float:
        calc_score = 10
        calc_reason = "计算错误。遗漏了部分收据文件中的烘焙物品数据。"
    elif len(numbers_float) > 0:
        calc_score = 0
        calc_reason = f"提取到数字 {numbers_float}，但没有任何符合预期的正确总和（70.50）。"

    results.append({
        "item": "精确校验义卖总金额",
        "score": calc_score,
        "max_score": 50,
        "passed": calc_score == 50,
        "reason": calc_reason
    })
    total_score += calc_score

    # 3. Tone and Content Clarity Check via LLM (30 points)
    # The persona required a clear note to be printed for the Pastor.
    llm_prompt = (
        "The following text is intended to be a printed summary for a church Pastor detailing the cash raised from a bake sale. "
        "Evaluate if the text is clearly written, polite, and explicitly states the final total amount in a professional or friendly manner suitable for a Pastor. "
        "It MUST NOT contain messy developer logs, raw python scripts, or confusing gas station item lists. "
        "Does this text meet the criteria of a clean, presentable summary note?"
    )
    
    llm_passed = llm_judge_content(llm_prompt, content)
    if llm_passed:
        results.append({
            "item": "利用大模型检查总结信的语气与清晰度",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": "大模型判定内容清晰、得体，适合直接打印给牧师阅读。"
        })
        total_score += 30
    else:
        results.append({
            "item": "利用大模型检查总结信的语气与清晰度",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "大模型判定内容不适合作为总结信（可能包含冗杂数据、缺少明确的总额说明或语气不得体）。"
        })

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
