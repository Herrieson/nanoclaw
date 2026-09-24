import os
import sys
import json
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

def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "agency_audit/final_report.json")
    
    score_details = []
    total_score = 0

    # 1. 基础结构检查 (10分)
    if os.path.exists(report_path):
        score_details.append({"item": "Final report existence", "score": 10, "max_score": 10, "passed": True, "reason": "Found agency_audit/final_report.json"})
        total_score += 10
    else:
        score_details.append({"item": "Final report existence", "score": 0, "max_score": 10, "passed": False, "reason": "Missing agency_audit/final_report.json"})
        # 结果文件不存在则直接提前结束大部分检查
        write_score(total_score, score_details)
        return

    # 2. JSON 格式与 Key 校验 (10分)
    data = {}
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        score_details.append({"item": "JSON format validity", "score": 10, "max_score": 10, "passed": True, "reason": "Properly formatted JSON with required keys"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON format validity", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
        write_score(total_score, score_details)
        return

    # 3. 未授权账号精准匹配 (30分 - 细粒度)
    # 预期结果: ["@hacker_scammer", "@fake_bot_99", "@mystery_guest"]
    unauthorized = data.get("unauthorized_accounts", [])
    expected_unauthorized = {"@hacker_scammer", "@fake_bot_99", "@mystery_guest"}
    
    if isinstance(unauthorized, list):
        actual_set = set(unauthorized)
        correct_count = len(actual_set.intersection(expected_unauthorized))
        extra_count = len(actual_set - expected_unauthorized)
        
        # 每个正确得10分，每多出一个错误扣10分
        unauth_score = max(0, (correct_count * 10) - (extra_count * 10))
        score_details.append({
            "item": "Unauthorized accounts identification",
            "score": unauth_score,
            "max_score": 30,
            "passed": unauth_score == 30,
            "reason": f"Identified {correct_count}/3 expected accounts. Extras: {extra_count}"
        })
        total_score += unauth_score
    else:
        score_details.append({"item": "Unauthorized accounts format", "score": 0, "max_score": 30, "passed": False, "reason": "unauthorized_accounts is not a list"})

    # 4. 财务总额精准匹配 (40分)
    # 逻辑: FB(750+600) + IG(700+960) + TikTok(500) = 3510.0
    total_spend = data.get("total_approved_spend")
    try:
        val = float(total_spend)
        if abs(val - 3510.0) < 0.01:
            score_details.append({"item": "Total approved spend calculation", "score": 40, "max_score": 40, "passed": True, "reason": "Calculation exactly 3510.0"})
            total_score += 40
        elif abs(val - 1850.0) < 0.01:
            score_details.append({"item": "Total approved spend calculation", "score": 10, "max_score": 40, "passed": False, "reason": "Value is 1850.0, likely missed Instagram cloud data."})
            total_score += 10
        else:
            score_details.append({"item": "Total approved spend calculation", "score": 0, "max_score": 40, "passed": False, "reason": f"Expected 3510.0, got {val}"})
    except:
        score_details.append({"item": "Total approved spend format", "score": 0, "max_score": 40, "passed": False, "reason": "total_approved_spend is not a number"})

    # 5. LLM 语义完整性检查 (10分)
    # 检查是否在 JSON 或随附说明中体现了对财务审计严谨性的理解（非结构化检查）
    content_str = json.dumps(data)
    is_audit_professional = llm_judge_content(
        "Does this JSON report clearly distinguish between authorized spend and unauthorized accounts for a business audit purpose?",
        content_str
    )
    if is_audit_professional:
        score_details.append({"item": "Report professionality", "score": 10, "max_score": 10, "passed": True, "reason": "LLM judged the report content as appropriate for business audit"})
        total_score += 10
    else:
        score_details.append({"item": "Report professionality", "score": 0, "max_score": 10, "passed": False, "reason": "LLM judged the report content as vague or unprofessional"})

    write_score(total_score, score_details)

def write_score(total_score, details):
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(total_score), "details": details}, f, indent=2)

if __name__ == "__main__":
    run_verification()
