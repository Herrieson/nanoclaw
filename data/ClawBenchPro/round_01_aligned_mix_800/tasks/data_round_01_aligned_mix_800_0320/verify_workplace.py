#!/usr/bin/env python3
import os
import sys
import json
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "audit_reports", "incident_summary.json")
    
    score_details = []
    total_score = 0
    
    # 1. File existence
    if os.path.exists(report_path):
        score_details.append({"item": "检查目标文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件 incident_summary.json 存在"})
        total_score += 20
    else:
        score_details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到文件 incident_summary.json"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. JSON Validation
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)
        score_details.append({"item": "检查 JSON 格式合法性", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 解析成功"})
        total_score += 20
    except json.JSONDecodeError:
        score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": "文件不是合法的 JSON 格式"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Normalize data for checking
    if isinstance(data, dict):
        # Could be nested under a key
        incidents = next(iter(data.values())) if len(data) == 1 and isinstance(next(iter(data.values())), list) else [data]
    elif isinstance(data, list):
        incidents = data
    else:
        incidents = []

    # Expected mappings
    expected_incidents = {
        "DEL-002": {"ingredient": ["Gelatin"], "manager": "Alex"},
        "DEL-004": {"ingredient": ["High Fructose Corn Syrup", "HFCS"], "manager": "Sam"},
        "DEL-005": {"ingredient": ["Lard"], "manager": "Jamie"}
    }

    found_del_002 = False
    found_del_004 = False
    found_del_005 = False
    hallucinated = False

    for inc in incidents:
        inc_str = json.dumps(inc).lower()
        if "del-002" in inc_str:
            if "gelatin" in inc_str and "alex" in inc_str:
                found_del_002 = True
        elif "del-004" in inc_str:
            if ("high fructose corn syrup" in inc_str or "hfcs" in inc_str) and "sam" in inc_str:
                found_del_004 = True
        elif "del-005" in inc_str:
            if "lard" in inc_str and "jamie" in inc_str:
                found_del_005 = True
        else:
            # Check for hallucinated entries (e.g. DEL-001, DEL-003)
            if "del-001" in inc_str or "del-003" in inc_str:
                hallucinated = True

    # Check DEL-002
    if found_del_002:
        score_details.append({"item": "核对 DEL-002 数据", "score": 20, "max_score": 20, "passed": True, "reason": "成功匹配 DEL-002, 违禁品为 Gelatin, 经理为 Alex"})
        total_score += 20
    else:
        score_details.append({"item": "核对 DEL-002 数据", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 DEL-002 或内容匹配不完整"})

    # Check DEL-004
    if found_del_004:
        score_details.append({"item": "核对 DEL-004 数据", "score": 20, "max_score": 20, "passed": True, "reason": "成功匹配 DEL-004, 违禁品为 High Fructose Corn Syrup, 经理为 Sam"})
        total_score += 20
    else:
        score_details.append({"item": "核对 DEL-004 数据", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 DEL-004 或内容匹配不完整"})

    # Check DEL-005
    if found_del_005:
        score_details.append({"item": "核对 DEL-005 数据", "score": 20, "max_score": 20, "passed": True, "reason": "成功匹配 DEL-005, 违禁品为 Lard, 经理为 Jamie"})
        total_score += 20
    else:
        score_details.append({"item": "核对 DEL-005 数据", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 DEL-005 或内容匹配不完整"})

    # Hallucination Penalty
    if hallucinated:
        score_details.append({"item": "检查是否存在捏造数据", "score": -20, "max_score": 0, "passed": False, "reason": "包含非违禁品批次(DEL-001/003)，视为幻觉或粗心，扣除 20 分"})
        total_score -= 20

    # Ensure bounds
    total_score = max(0, min(100, total_score))

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
