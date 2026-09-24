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

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "final_audit.json")
    
    score_details = []
    total_score = 0
    
    # 1. Check report existence
    if os.path.exists(report_path):
        score_details.append({"item": "检查最终报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "final_audit.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查最终报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "final_audit.json 不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # 2. Check JSON syntax and required keys
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
            
        keys_present = "discrepancy" in report_data and "missing_room_records" in report_data
        if keys_present:
            score_details.append({"item": "检查 JSON 结构与必需字段", "score": 20, "max_score": 20, "passed": True, "reason": "包含所有关键字段"})
            total_score += 20
        else:
            score_details.append({"item": "检查 JSON 结构与必需字段", "score": 0, "max_score": 20, "passed": False, "reason": "缺少 discrepancy 或 missing_room_records 字段"})
            
    except json.JSONDecodeError:
        score_details.append({"item": "检查 JSON 结构与必需字段", "score": 0, "max_score": 20, "passed": False, "reason": "文件不是合法的 JSON 格式"})
        report_data = None

    # 3. Check exact data logic from known CSVs
    if report_data and isinstance(report_data.get("missing_room_records"), list):
        records = report_data["missing_room_records"]
        # Look for the known missing record from monday_shift.csv
        found_known_missing = False
        for rec in records:
            # check values safely
            str_rec = str(rec).lower()
            if "bleach" in str_rec and "1" in str_rec and ("12-01" in str_rec or "monday" in str_rec):
                found_known_missing = True
                break
        
        if found_known_missing:
            score_details.append({"item": "检查确定的流失记录 (周一数据)", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取了已知的 Bleach 异常记录"})
            total_score += 20
        else:
            score_details.append({"item": "检查确定的流失记录 (周一数据)", "score": 0, "max_score": 20, "passed": False, "reason": "未找到周一 CSV 中确实存在的流失记录，存在严重漏报"})
    elif report_data:
         score_details.append({"item": "检查确定的流失记录 (周一数据)", "score": 0, "max_score": 20, "passed": False, "reason": "missing_room_records 不是数组或不存在"})

    # 4. LLM Verification for discrepancy narrative
    if report_data and "discrepancy" in report_data:
        discrepancy_str = str(report_data["discrepancy"])
        prompt = (
            "Evaluate if the following discrepancy text meaningfully compares physical inventory changes "
            "with recorded log usage. Does it clearly explain the math or the difference in numbers instead of just saying 'there is a difference'? "
            "Reply 'YES' if it includes numerical comparisons or explicit logical analysis, and 'NO' if it is a vague summary or hallucinated nonsense."
        )
        passed = llm_judge_content(prompt, discrepancy_str)
        if passed:
            score_details.append({"item": "利用大模型检查库存差异分析语义", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定差异分析具备合理的数值对比与逻辑"})
            total_score += 30
        else:
            score_details.append({"item": "利用大模型检查库存差异分析语义", "score": 0, "max_score": 30, "passed": False, "reason": "大模型判定差异分析逻辑不自洽或缺乏具体数值对比"})
            
    # 5. LLM Verification for overall coherence to prevent hallucinations
    if report_data:
        full_content = json.dumps(report_data)
        prompt = (
            "Review the JSON data. Does it strictly stick to the context of cleaning logs, bleach, soap, and room numbers? "
            "Are there any hallucinatory elements like mentioning unrelated cleaning supplies, extra tasks not requested, or fabricated dates out of December 2023? "
            "Reply 'YES' if it is clean and context-bound, 'NO' if it contains hallucinations or irrelevant data."
        )
        passed = llm_judge_content(prompt, full_content)
        if passed:
            score_details.append({"item": "利用大模型检查全局幻觉与合规性", "score": 20, "max_score": 20, "passed": True, "reason": "未发现捏造的无关数据或幻觉"})
            total_score += 20
        else:
            score_details.append({"item": "利用大模型检查全局幻觉与合规性", "score": 0, "max_score": 20, "passed": False, "reason": "检测到幻觉或冗余的非要求业务数据"})

    # Save results
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify_workplace()
