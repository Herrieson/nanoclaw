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
    score_details = []
    total_score = 0
    
    report_path = os.path.join(workspace, "final_drop", "audit_report.json")
    
    # 1. Check if file exists and is valid JSON (10 pts)
    if not os.path.exists(report_path):
        score_details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "audit_report.json 不存在"})
        write_score(0, score_details)
        return
        
    try:
        with open(report_path, "r") as f:
            report_data = json.load(f)
        score_details.append({"item": "检查报告文件是否存在且为合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且格式正确"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "检查报告文件是否存在且为合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        write_score(0, score_details)
        return

    # 2. Check JSON schema and keys (10 pts)
    required_keys = ["missing_depositions", "unscheduled_depositions", "unauthorized_appearances"]
    if all(k in report_data for k in required_keys):
        score_details.append({"item": "检查必需的JSON字段是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有所需字段"})
        total_score += 10
    else:
        score_details.append({"item": "检查必需的JSON字段是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少核心分类字段"})

    report_str = json.dumps(report_data, indent=2)

    # 3. Missing Depositions Check (30 pts)
    # Expected missing: 2023-11-01 Doe v. City, 2023-11-03 Smith v. State, 2023-11-04 Zeta v. Omega
    missing_prompt = (
        "Check if the JSON data under 'missing_depositions' accurately lists ALL the following three sessions "
        "(they might be formatted as strings or objects, just verify the core facts are present): "
        "1. Date: 2023-11-01, Case: Doe v. City "
        "2. Date: 2023-11-03, Case: Smith v. State "
        "3. Date: 2023-11-04, Case: Zeta v. Omega "
        "And NO OTHER missing sessions are fabricated."
    )
    if llm_judge_content(missing_prompt, report_str):
        score_details.append({"item": "检查缺失的日程(missing_depositions)是否完全正确", "score": 30, "max_score": 30, "passed": True, "reason": "准确找出了3个缺失的日程"})
        total_score += 30
    else:
        score_details.append({"item": "检查缺失的日程(missing_depositions)是否完全正确", "score": 0, "max_score": 30, "passed": False, "reason": "缺失记录不匹配或存在幻觉"})

    # 4. Unscheduled Depositions Check (30 pts)
    # Expected ghost: 2023-11-05 Alpha v. Beta, 2023-11-06 Smith v. State
    ghost_prompt = (
        "Check if the JSON data under 'unscheduled_depositions' accurately lists ALL the following two sessions: "
        "1. Date: 2023-11-05, Case: Alpha v. Beta "
        "2. Date: 2023-11-06, Case: Smith v. State "
        "And NO OTHER unscheduled sessions are fabricated."
    )
    if llm_judge_content(ghost_prompt, report_str):
        score_details.append({"item": "检查未计划的记录(unscheduled_depositions)是否完全正确", "score": 30, "max_score": 30, "passed": True, "reason": "准确找出了2个幽灵记录"})
        total_score += 30
    else:
        score_details.append({"item": "检查未计划的记录(unscheduled_depositions)是否完全正确", "score": 0, "max_score": 30, "passed": False, "reason": "未计划的记录不匹配或存在幻觉"})

    # 5. Unauthorized Appearances Check (20 pts)
    # Expected unauthorized: 2023-11-06 Smith v. State (Lead: Paralegal Miller)
    miller_prompt = (
        "Check if the JSON data under 'unauthorized_appearances' explicitly flags the session involving 'Miller' "
        "(or Case: Smith v. State on 2023-11-06) as unauthorized. NO OTHER authorized personnel should be flagged."
    )
    if llm_judge_content(miller_prompt, report_str):
        score_details.append({"item": "检查越权行为(unauthorized_appearances)是否正确", "score": 20, "max_score": 20, "passed": True, "reason": "准确识别了 Miller 的越权行为"})
        total_score += 20
    else:
        score_details.append({"item": "检查越权行为(unauthorized_appearances)是否正确", "score": 0, "max_score": 20, "passed": False, "reason": "未能准确识别 Miller 记录或存在误判"})

    write_score(total_score, score_details)

def write_score(total, details):
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
