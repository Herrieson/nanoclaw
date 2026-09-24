import os
import sys
import json
import glob
import re
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

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

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    audit_dir = os.path.join(workspace, "final_audit")
    
    score_details = []
    total_score = 0
    
    # 1. Check Directory and Report Existence (10 points)
    report_files = []
    if os.path.exists(audit_dir) and os.path.isdir(audit_dir):
        report_files = glob.glob(os.path.join(audit_dir, "*.txt")) + glob.glob(os.path.join(audit_dir, "*.md"))
        
    if report_files:
        score_details.append({"item": "检查报告目录与文件存在性", "score": 10, "max_score": 10, "passed": True, "reason": f"找到报告文件: {report_files[0]}"})
        total_score += 10
        with open(report_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        score_details.append({"item": "检查报告目录与文件存在性", "score": 0, "max_score": 10, "passed": False, "reason": "未在 final_audit/ 下找到 .txt 或 .md 报告文件"})
        content = ""

    if not content:
        # If no content, write 0 for the rest and exit
        for item in ["精准提取非法供应商名单", "提取已到货合法订单总额", "提取未到货合法订单总额", "LLM评估语义逻辑与报告质量"]:
            score_details.append({"item": item, "score": 0, "max_score": 20, "passed": False, "reason": "文件为空或不存在"})
        return {"total_score": total_score, "details": score_details}

    # 2. Extract Illegal Suppliers (30 points)
    # They should explicitly mention "Cheap Junk Wood Co." and "Unknown Scraps"
    has_cheap_junk = "Cheap Junk Wood Co." in content or "Cheap Junk" in content
    has_unknown = "Unknown Scraps" in content
    illegal_score = 0
    if has_cheap_junk and has_unknown:
        illegal_score = 30
        reason = "准确列出了所有不合规/未注册的供应商"
    elif has_cheap_junk or has_unknown:
        illegal_score = 15
        reason = "仅列出了部分不合规的供应商"
    else:
        reason = "未能识别出不合规的供应商"
    score_details.append({"item": "精准提取非法供应商名单", "score": illegal_score, "max_score": 30, "passed": illegal_score == 30, "reason": reason})
    total_score += illegal_score

    # 3. Calculate "Arrived" Valid Orders (30 points)
    # Valid & Arrived: INV-001 (1200) + INV-002 (4500) = 5700
    # Search for number 5700 exactly
    num_matches = re.findall(r'\b5,?700(?:\.00)?\b', content)
    if num_matches:
        score_details.append({"item": "提取已到货合法订单总额", "score": 30, "max_score": 30, "passed": True, "reason": "精准计算并提取到已到货金额 5700"})
        total_score += 30
    else:
        score_details.append({"item": "提取已到货合法订单总额", "score": 0, "max_score": 30, "passed": False, "reason": "未能计算或提取到正确的已到货金额(应为5700)"})

    # 4. Calculate "Not Arrived" Valid Orders (20 points)
    # Valid & Not Arrived: INV-004 (2100)
    # Search for number 2100 exactly
    num_matches_not_arrived = re.findall(r'\b2,?100(?:\.00)?\b', content)
    if num_matches_not_arrived:
        score_details.append({"item": "提取未到货合法订单总额", "score": 20, "max_score": 20, "passed": True, "reason": "精准计算并提取到未到货金额 2100"})
        total_score += 20
    else:
        score_details.append({"item": "提取未到货合法订单总额", "score": 0, "max_score": 20, "passed": False, "reason": "未能计算或提取到正确的未到货金额(应为2100)"})

    # 5. LLM Evaluation for Semantic Formatting (10 points)
    prompt = (
        "Does the report clearly separate the calculation of 'arrived' orders and 'not arrived' orders, "
        "and is it written in a concise and clear summary format suitable for a construction foreman?"
    )
    llm_passed = llm_judge_content(prompt, content)
    if llm_passed:
        score_details.append({"item": "LLM评估语义逻辑与报告质量", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定报告结构清晰且语气合适"})
        total_score += 10
    else:
        score_details.append({"item": "LLM评估语义逻辑与报告质量", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定报告未能清晰区分两类款项或语气不佳"})

    return {"total_score": total_score, "details": score_details}

if __name__ == "__main__":
    result = verify_workplace()
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
