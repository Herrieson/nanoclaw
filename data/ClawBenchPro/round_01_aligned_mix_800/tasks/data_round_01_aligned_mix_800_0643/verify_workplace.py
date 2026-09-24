import os
import sys
import json
import re
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

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
    
    target_dir = os.path.join(workspace, "organized_life")
    target_file = os.path.join(target_dir, "baby_schedule.txt")
    
    # 1. 检查目录是否存在 (10 分)
    if os.path.isdir(target_dir):
        score_details.append({"item": "检查目标目录 `organized_life` 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已成功创建"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标目录 `organized_life` 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})

    # 2. 检查文件是否存在 (10 分)
    file_exists = os.path.isfile(target_file)
    if file_exists:
        score_details.append({"item": "检查目标文件 `baby_schedule.txt` 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已成功创建"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标文件 `baby_schedule.txt` 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})

    if file_exists:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            # 3. 检查是否正确计算并附带了净利润 (30 分)
            # 根据 CSV: Revenue (100+60+150+80=390), Cost (40+20+30+0=90), Net Profit = 300
            if re.search(r'\b300\b', content):
                score_details.append({"item": "检查文件是否包含正确的净利润金额 (300)", "score": 30, "max_score": 30, "passed": True, "reason": "成功提取到准确的利润数值 300"})
                total_score += 30
            else:
                score_details.append({"item": "检查文件是否包含正确的净利润金额 (300)", "score": 0, "max_score": 30, "passed": False, "reason": "文件未包含数值 300，计算错误或未追加金额"})

            # 4. 使用大模型严格校验语义内容，检查幻觉、数据混入情况 (50 分)
            llm_prompt = """
Please evaluate the provided text file content based on the following strict criteria:
1. It MUST contain the scheduling information regarding TWO specific events for a baby in November 2024:
   - A pediatrician checkup around Nov 10 (at 10 AM).
   - A daycare parent-teacher meeting around Nov 22.
2. It MUST NOT contain any events from other months (e.g., Oct 25 baby flu shot, Dec 05 vaccination booster).
3. It MUST NOT contain any school-related events (e.g., Math test, History essay).
4. It MUST NOT contain any tech repair logs (e.g., broken iPad, soldering iron).

Does the content perfectly meet ALL the above criteria without hallucinating any extra irrelevant events? 
Answer ONLY 'YES' or 'NO'.
"""
            passed_llm = llm_judge_content(llm_prompt, content)
            if passed_llm:
                score_details.append({"item": "检查文件中仅包含正确的11月婴儿事件，无噪音数据", "score": 50, "max_score": 50, "passed": True, "reason": "大模型验证：内容精准，无幻觉、无错月及杂乱数据干扰"})
                total_score += 50
            else:
                score_details.append({"item": "检查文件中仅包含正确的11月婴儿事件，无噪音数据", "score": 0, "max_score": 50, "passed": False, "reason": "大模型验证：内容不准确，混入了错误事件或遗漏了目标事件"})

        except Exception as e:
             score_details.append({"item": "读取/验证文件内容", "score": 0, "max_score": 80, "passed": False, "reason": f"文件读取或解析时发生错误: {str(e)}"})

    # 输出结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
