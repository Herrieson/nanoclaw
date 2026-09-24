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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "deliverables", "audit_report.json")
    
    total_score = 0
    details = []

    # Check 1: File Existence
    if os.path.exists(report_path):
        total_score += 10
        details.append({"item": "检查报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 deliverables/audit_report.json 存在"})
    else:
        details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 deliverables/audit_report.json 不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # Check 2: Valid JSON
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
            report_content = json.dumps(report_data, ensure_ascii=False)
        total_score += 10
        details.append({"item": "检查报告格式是否为有效 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件可解析为 JSON"})
    except Exception as e:
        details.append({"item": "检查报告格式是否为有效 JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # Check 3: Extract Total Value (Strictly Code)
    # Expected Value: Oak(1500) + Maple(2560) + Ebony(12000) + Mahogany(5400) + Cedar(1800) = 23260
    extracted_value = None
    for key, val in report_data.items():
        if isinstance(val, (int, float)):
            if 23000 < val < 24000: # Heuristic to find the field without knowing the exact key name
                extracted_value = val
                break
        elif isinstance(val, str) and "23260" in val:
            extracted_value = 23260
            break

    if extracted_value == 23260:
        total_score += 40
        details.append({"item": "检查符合代码的木材总价值", "score": 40, "max_score": 40, "passed": True, "reason": "总价值准确为 23260"})
    else:
        # Check if they included Pine by mistake (Pine = 900)
        details.append({"item": "检查符合代码的木材总价值", "score": 0, "max_score": 40, "passed": False, "reason": f"未能找到准确的总价值 (期望: 23260)。报告提取的值: {extracted_value}"})

    # Check 4: Non-compliant items (Strictly Code)
    # Expected: Pine or ID_005
    has_pine = False
    report_str = str(report_data).lower()
    if "pine" in report_str or "id_005" in report_str:
        has_pine = True
    
    if has_pine:
        total_score += 20
        details.append({"item": "检查不合规项目清单", "score": 20, "max_score": 20, "passed": True, "reason": "成功捕捉到不合规项目 Pine (ID_005)"})
    else:
        details.append({"item": "检查不合规项目清单", "score": 0, "max_score": 20, "passed": False, "reason": "未捕捉到不合规项目 Pine (ID_005)"})

    # Check 5: Abnormal unit price annotation using LLM (LLM Semantic Check)
    # Expected: Mentioning Ebony or ID_006 or 6000 over 5000.
    prompt_text = "Does the following JSON content explicitly mention an 'abnormal' or 'high' unit price exceeding 5000 dollars, specifically regarding 'Ebony' or 'ID_006' or a price of 6000?"
    llm_passed = llm_judge_content(prompt_text, report_content)
    
    if llm_passed:
        total_score += 20
        details.append({"item": "利用大模型检查异常单价特殊标注", "score": 20, "max_score": 20, "passed": True, "reason": "报告中成功标注了超过 5000 的异常单价项目 (Ebony)"})
    else:
        details.append({"item": "利用大模型检查异常单价特殊标注", "score": 0, "max_score": 20, "passed": False, "reason": "报告中未明确标注异常单价 (缺少对 Ebony / ID_006 或 6000的警示)"})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
