import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# 🔒 强制 API 规范
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
    deliverables_path = os.path.join(workspace, "deliverables")
    score_details = []
    
    # 1. 检查目录结构 (10分)
    if os.path.exists(deliverables_path) and os.path.isdir(deliverables_path):
        score_details.append({"item": "Deliverables directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory found."})
    else:
        score_details.append({"item": "Deliverables directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory missing."})

    # 2. 检查结果文件内容与逻辑 (结构化检查)
    # 预期的正确数据计算：
    # Alice: 4 + 2 = 6
    # Bob: 3 + 2 = 5 (invalid_data 应当被剔除)
    # Charlie: 2.5
    # Diana: 6
    # Unauthorized: Unknown Stranger, Intruder Ivan
    
    report_file = None
    for f in os.listdir(deliverables_path) if os.path.exists(deliverables_path) else []:
        if f.endswith((".json", ".txt", ".md", ".csv")):
            report_file = os.path.join(deliverables_path, f)
            break
            
    if not report_file:
        score_details.append({"item": "Summary report file generated", "score": 0, "max_score": 90, "passed": False, "reason": "No report file found in deliverables."})
    else:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 2a. 检查非授权人员名单 (30分)
        unauthorized_check = ("Unknown Stranger" in content) and ("Intruder Ivan" in content)
        if unauthorized_check:
            score_details.append({"item": "Identify unauthorized participants", "score": 30, "max_score": 30, "passed": True, "reason": "Both unauthorized names identified."})
        elif "Unknown Stranger" in content or "Intruder Ivan" in content:
            score_details.append({"item": "Identify unauthorized participants", "score": 15, "max_score": 30, "passed": False, "reason": "Only partial unauthorized names identified."})
        else:
            score_details.append({"item": "Identify unauthorized participants", "score": 0, "max_score": 30, "passed": False, "reason": "No unauthorized names found."})

        # 2b. 检查批准人员的小时数计算 (精准匹配 - 40分)
        # 我们使用 LLM 来从非结构化或半结构化报告中提取数值并验证逻辑
        prompt = """
        Analyze the report and extract the total hours for the following approved volunteers:
        - Alice Smith
        - Bob Johnson
        - Charlie Brown
        - Diana Prince
        Verify if the report matches these EXACT values: Alice: 6, Bob: 5, Charlie: 2.5, Diana: 6.
        Note: If Bob's hours are 8 (incorrectly including 'invalid_data') or 3 (missing data), it is WRONG.
        Does the report contain these correct totals?
        """
        if llm_judge_content(prompt, content):
            score_details.append({"item": "Accurate hours calculation (filtering dirty data)", "score": 40, "max_score": 40, "passed": True, "reason": "Calculation logic and data cleaning are correct."})
        else:
            score_details.append({"item": "Accurate hours calculation (filtering dirty data)", "score": 0, "max_score": 40, "passed": False, "reason": "Calculation incorrect or failed to filter dirty data (e.g. Bob's hours)."})

        # 2c. 报告正式性与格式 (LLM 语义检查 - 20分)
        persona_prompt = "Is the report written in a formal, professional tone suitable for a university Dean, and does it clearly separate unauthorized people from the approved summary?"
        if llm_judge_content(persona_prompt, content):
            score_details.append({"item": "Formal report tone and structure", "score": 20, "max_score": 20, "passed": True, "reason": "Tone is appropriate for a Dean."})
        else:
            score_details.append({"item": "Formal report tone and structure", "score": 5, "max_score": 20, "passed": False, "reason": "Tone is too casual or structure is messy."})

    total_score = sum(item["score"] for item in score_details)
    
    output = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    verify()
