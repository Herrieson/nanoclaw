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
    final_audit_dir = os.path.join(workspace, "final_audit")
    
    score_details = []
    total_score = 0

    # 1. Check directory existence
    passed_dir = os.path.isdir(final_audit_dir)
    score = 10 if passed_dir else 0
    total_score += score
    score_details.append({
        "item": "检查目录 final_audit 是否存在",
        "score": score,
        "max_score": 10,
        "passed": passed_dir,
        "reason": "目录 final_audit 存在" if passed_dir else "目录 final_audit 不存在"
    })

    if not passed_dir:
        # 提前结束
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Read all contents from final_audit
    audit_files = []
    all_content = ""
    for root, _, files in os.walk(final_audit_dir):
        for file in files:
            file_path = os.path.join(root, file)
            audit_files.append(file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    all_content += f"\n--- File: {file} ---\n"
                    all_content += f.read()
            except Exception:
                pass
                
    passed_files = len(audit_files) > 0
    score_details.append({
        "item": "检查 final_audit 目录下是否有输出文件",
        "score": 10 if passed_files else 0,
        "max_score": 10,
        "passed": passed_files,
        "reason": f"找到 {len(audit_files)} 个文件" if passed_files else "目录为空"
    })
    if passed_files:
        total_score += 10

    if not passed_files:
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. Use LLM to check for exact illegal suppliers
    prompt_illegal = (
        "Check if the document explicitly lists the EXACT illegal suppliers (those not in the approved whitelist but present in invoices). "
        "The correct illegal suppliers are EXACTLY 'Cheap Junk Wood Co.' and 'Unknown Scraps'. "
        "Does the content clearly identify both of these as illegal or unapproved? Answer YES only if BOTH are clearly identified and no valid suppliers (like Redwood Supplies, Oak & Iron, Bay Area Lumber) are mistakenly listed as illegal."
    )
    passed_illegal = llm_judge_content(prompt_illegal, all_content)
    score_details.append({
        "item": "准确找出所有非法供应商且无误判",
        "score": 30 if passed_illegal else 0,
        "max_score": 30,
        "passed": passed_illegal,
        "reason": "正确列出了非法供应商" if passed_illegal else "未正确列出非法供应商或混入合法供应商"
    })
    if passed_illegal:
        total_score += 30

    # 4. Use LLM to check arrived/received owed amount
    prompt_arrived = (
        "Check if the document explicitly states the owed amount for 'arrived' or 'received' orders from approved suppliers. "
        "The correct calculation is 1200 + 4500 = 5700. "
        "Does the text explicitly say the amount for arrived/received is exactly 5700? Answer YES or NO."
    )
    passed_arrived = llm_judge_content(prompt_arrived, all_content)
    score_details.append({
        "item": "正确计算已签收/到货的白名单供应商欠款",
        "score": 20 if passed_arrived else 0,
        "max_score": 20,
        "passed": passed_arrived,
        "reason": "已到货欠款 5700 计算正确" if passed_arrived else "未找到正确的已到货欠款(5700)"
    })
    if passed_arrived:
        total_score += 20

    # 5. Use LLM to check pending/not arrived owed amount
    prompt_pending = (
        "Check if the document explicitly states the owed amount for 'pending' or 'not arrived' or 'not received' orders from approved suppliers. "
        "The correct calculation is exactly 2100. "
        "Does the text explicitly say the amount for not arrived/pending is exactly 2100? Answer YES or NO."
    )
    passed_pending = llm_judge_content(prompt_pending, all_content)
    score_details.append({
        "item": "正确计算未到货的白名单供应商欠款",
        "score": 20 if passed_pending else 0,
        "max_score": 20,
        "passed": passed_pending,
        "reason": "未到货欠款 2100 计算正确" if passed_pending else "未找到正确的未到货欠款(2100)"
    })
    if passed_pending:
        total_score += 20

    # 6. Use LLM to check tone and report presence
    prompt_tone = (
        "Read the report. Does it contain a summary directed at the carpentry manager? "
        "The tone should be clear, concise, and helpful to ease the manager's anxiety. "
        "Answer YES if there is a proper report summarizing the findings, and NO if it is just a raw data dump without any contextual summary."
    )
    passed_tone = llm_judge_content(prompt_tone, all_content)
    score_details.append({
        "item": "总结报告包含适当的安抚语气和完整的业务回复",
        "score": 10 if passed_tone else 0,
        "max_score": 10,
        "passed": passed_tone,
        "reason": "报告语气适宜且概括完整" if passed_tone else "缺乏具有针对性的报告总结"
    })
    if passed_tone:
        total_score += 10

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
