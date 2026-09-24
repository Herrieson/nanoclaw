import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    # 此函数为检测非结构化文本的统一接口
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

def verify(workspace):
    details = []
    total_score = 0
    
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    # 1. 检查 deliverables 目录是否存在
    if os.path.isdir(deliverables_dir):
        details.append({"item": "Check if 'deliverables' directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory 'deliverables' exists."})
        total_score += 10
    else:
        details.append({"item": "Check if 'deliverables' directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'deliverables' is missing."})
        
    # 2. 检查目录下是否有报告文件
    report_content = ""
    if os.path.isdir(deliverables_dir):
        files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
        if files:
            details.append({"item": "Check if report file exists in 'deliverables'", "score": 10, "max_score": 10, "passed": True, "reason": f"Found file(s): {', '.join(files)}"})
            total_score += 10
            # Read the first file assuming it's the report
            with open(os.path.join(deliverables_dir, files[0]), 'r', encoding='utf-8') as f:
                report_content = f.read()
        else:
            details.append({"item": "Check if report file exists in 'deliverables'", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'deliverables' is empty."})
    else:
        details.append({"item": "Check if report file exists in 'deliverables'", "score": 0, "max_score": 10, "passed": False, "reason": "Cannot check files, directory does not exist."})

    # If we have report content, use LLM to check specific constraints
    if report_content:
        # 3. 检查合法金额 1050.75
        prompt_amount = "Does the following text clearly state that the total legitimate/approved expenses amount to exactly 1050.75? (Do not accept amounts other than 1050.75)"
        if llm_judge_content(prompt_amount, report_content):
            details.append({"item": "Check if report contains correct total approved amount (1050.75)", "score": 30, "max_score": 30, "passed": True, "reason": "Report correctly states the total approved amount."})
            total_score += 30
        else:
            details.append({"item": "Check if report contains correct total approved amount (1050.75)", "score": 0, "max_score": 30, "passed": False, "reason": "Report fails to state the exact total approved amount of 1050.75."})
            
        # 4. 检查鸟类观察者名单 Bob Smith, Charlie Davis, Frank Castle
        prompt_names = "Does the following text list EXACTLY these three individuals as the ones who submitted expenses for bird-watching gear: Bob Smith, Charlie Davis, and Frank Castle?"
        if llm_judge_content(prompt_names, report_content):
            details.append({"item": "Check if report contains the correct list of bird-watchers", "score": 30, "max_score": 30, "passed": True, "reason": "Report correctly lists Bob Smith, Charlie Davis, and Frank Castle."})
            total_score += 30
        else:
            details.append({"item": "Check if report contains the correct list of bird-watchers", "score": 0, "max_score": 30, "passed": False, "reason": "Report does not accurately list the required individuals."})

        # 5. 检查信件整体语气和目的
        prompt_tone = "Does the following text read like a summary report addressed to HR, summarizing expenses and attendees? Is it professional and clear?"
        if llm_judge_content(prompt_tone, report_content):
            details.append({"item": "Check report tone and clarity", "score": 20, "max_score": 20, "passed": True, "reason": "Report maintains a professional and appropriate tone."})
            total_score += 20
        else:
            details.append({"item": "Check report tone and clarity", "score": 0, "max_score": 20, "passed": False, "reason": "Report tone is inappropriate or lacks clarity."})
    else:
        details.append({"item": "Check if report contains correct total approved amount (1050.75)", "score": 0, "max_score": 30, "passed": False, "reason": "No report content found."})
        details.append({"item": "Check if report contains the correct list of bird-watchers", "score": 0, "max_score": 30, "passed": False, "reason": "No report content found."})
        details.append({"item": "Check report tone and clarity", "score": 0, "max_score": 20, "passed": False, "reason": "No report content found."})

    score_result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace_path)
