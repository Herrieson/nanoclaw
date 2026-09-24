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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "archive_report")
    
    score_details = []
    total_score = 0
    
    # 1. Directory Existence (10 points)
    if os.path.isdir(report_dir):
        score_details.append({"item": "检查结果目录 archive_report 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录 archive_report 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # Gather all text content from the report directory
    all_text = ""
    for root, _, files in os.walk(report_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    all_text += f.read() + "\n"
            except:
                pass

    if not all_text.strip():
        score_details.append({"item": "检查结果目录是否包含文件", "score": 0, "max_score": 90, "passed": False, "reason": "目录为空或文件无法读取"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # 2. Check for unique valid records (30 points)
    # The valid call numbers that should be extracted (ESP-003 might be excluded if Agent thought "Missing Title Book" is an invalid title literal, so we accept both 6 and 7 total records)
    required_ids = {"ESP-001", "ESP-002", "ESP-004", "ESP-005", "ESP-006", "ESP-007"}
    found_ids = [cid for cid in required_ids if cid in all_text]
    
    if len(found_ids) == 6:
        score_details.append({"item": "提取合法且去重后的核心档案记录", "score": 30, "max_score": 30, "passed": True, "reason": f"成功提取所有目标记录 ({len(found_ids)}/6)"})
        total_score += 30
    elif len(found_ids) > 0:
        partial_score = len(found_ids) * 5
        score_details.append({"item": "提取合法且去重后的核心档案记录", "score": partial_score, "max_score": 30, "passed": False, "reason": f"部分记录缺失，仅找到 ({len(found_ids)}/6)"})
        total_score += partial_score
    else:
        score_details.append({"item": "提取合法且去重后的核心档案记录", "score": 0, "max_score": 30, "passed": False, "reason": "未能在输出文件中找到有效的记录编号"})

    # 3. Check calculation results (30 points)
    # Cost should be 6 * 12.50 = 75.00 OR 7 * 12.50 = 87.50 depending on how ESP-003 was handled.
    # We will use regex to find the numeric representation.
    cost_matches = re.findall(r'75\.?0*|87\.50*', all_text)
    if cost_matches:
        score_details.append({"item": "精准验证恢复项目的预算成本计算", "score": 30, "max_score": 30, "passed": True, "reason": f"找到正确的成本核算值: {cost_matches[0]}"})
        total_score += 30
    else:
        score_details.append({"item": "精准验证恢复项目的预算成本计算", "score": 0, "max_score": 30, "passed": False, "reason": "未能找到正确的成本计算结果 ($75.00 或 $87.50)"})

    # 4. LLM Semantic Check for summary narrative (30 points)
    prompt = """Please verify if the following file content satisfies all criteria:
1. It contains a narrative summary of the library digitization project.
2. It explicitly mentions the number of good records, the number of duplicates found, and the final budget/cost.
3. It adopts a professional, reassuring, and slightly empathetic tone suitable for returning to an overwhelmed local archive assistant."""
    
    llm_passed = llm_judge_content(prompt, all_text)
    if llm_passed:
        score_details.append({"item": "利用大模型检查总结报告的业务语义与情绪对齐", "score": 30, "max_score": 30, "passed": True, "reason": "报告内容完整，语调恰当，且包含对各项统计的业务叙述"})
        total_score += 30
    else:
        score_details.append({"item": "利用大模型检查总结报告的业务语义与情绪对齐", "score": 0, "max_score": 30, "passed": False, "reason": "大模型判定报告缺失关键叙述，或语气不符合被分配的角色要求"})

    # Write output
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
