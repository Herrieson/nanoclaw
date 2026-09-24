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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "deliverables", "audit_report.json")
    
    total_score = 0
    details = []

    # 1. Check directory (10 pts)
    deliverables_dir = os.path.join(workspace, "deliverables")
    if os.path.isdir(deliverables_dir):
        details.append({"item": "检查 deliverables 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})

    # 2. Check file existence (10 pts)
    if os.path.isfile(report_path):
        details.append({"item": "检查 audit_report.json 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "检查 audit_report.json 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        
    if not os.path.isfile(report_path):
        write_score(total_score, details)
        return

    # 3. Check JSON schema validity (10 pts)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        details.append({"item": "检查文件是否为合法 JSON 格式", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析为 JSON"})
        total_score += 10
    except Exception as e:
        details.append({"item": "检查文件是否为合法 JSON 格式", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        write_score(total_score, details)
        return

    report_content_str = json.dumps(report_data, indent=2, ensure_ascii=False)

    # 4. LLM Check: Unscheduled depositions (20 pts)
    prompt_unscheduled = "Does this JSON explicitly list 'Doe v. City' (2023-10-02) and 'Smith v. State' (2023-10-02) under a category indicating they were UNSCHEDULED or occurred without being on the master schedule? (Must mention both)."
    if llm_judge_content(prompt_unscheduled, report_content_str):
        details.append({"item": "检查是否准确抓取并分类'未排期但已进行的庭审'", "score": 20, "max_score": 20, "passed": True, "reason": "成功分类 Doe v. City 与 Smith v. State"})
        total_score += 20
    else:
        details.append({"item": "检查是否准确抓取并分类'未排期但已进行的庭审'", "score": 0, "max_score": 20, "passed": False, "reason": "未能准确指出未排期的案件详情"})

    # 5. LLM Check: Scheduled but missing transcripts (20 pts)
    prompt_missing = "Does this JSON explicitly list 'Roe v. Inc' (2023-10-02) and 'Smith v. State' (2023-10-03) under a category indicating they were SCHEDULED BUT MISSING transcripts? (Must mention both)."
    if llm_judge_content(prompt_missing, report_content_str):
        details.append({"item": "检查是否准确抓取并分类'已排期但缺失记录的庭审'", "score": 20, "max_score": 20, "passed": True, "reason": "成功分类 Roe v. Inc 与 Smith v. State 缺失"})
        total_score += 20
    else:
        details.append({"item": "检查是否准确抓取并分类'已排期但缺失记录的庭审'", "score": 0, "max_score": 20, "passed": False, "reason": "未能准确指出缺失庭审记录的案件详情"})

    # 6. LLM Check: Unauthorized appearance (30 pts)
    prompt_unauthorized = "Does this JSON explicitly flag 'Paralegal Miller' in the 'Smith v. State' case under an UNAUTHORIZED appearance category or similar strict warning?"
    if llm_judge_content(prompt_unauthorized, report_content_str):
        details.append({"item": "检查是否准确预警了'Paralegal Miller'的未授权出庭", "score": 30, "max_score": 30, "passed": True, "reason": "成功捕获并警告 Paralegal Miller"})
        total_score += 30
    else:
        details.append({"item": "检查是否准确预警了'Paralegal Miller'的未授权出庭", "score": 0, "max_score": 30, "passed": False, "reason": "漏掉了严重违规的 Paralegal Miller"})

    write_score(total_score, details)

def write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
