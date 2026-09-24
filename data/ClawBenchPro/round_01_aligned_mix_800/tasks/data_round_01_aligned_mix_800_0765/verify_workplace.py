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

def verify_workplace(workspace):
    score_details = []
    total_score = 0
    report_dir = os.path.join(workspace, "final_report")

    # 1. 检查目录
    if os.path.isdir(report_dir):
        score_details.append({"item": "检查 final_report 目录是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "final_report 目录存在"})
        total_score += 20
    else:
        score_details.append({"item": "检查 final_report 目录是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "final_report 目录不存在"})
        
    # 2. 检查输出文件
    report_content = ""
    file_found = False
    if os.path.isdir(report_dir):
        files = os.listdir(report_dir)
        files = [f for f in files if os.path.isfile(os.path.join(report_dir, f))]
        if files:
            file_found = True
            with open(os.path.join(report_dir, files[0]), "r", encoding="utf-8") as f:
                report_content = f.read()
            score_details.append({"item": "检查是否在目录中创建了文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到了文件 {files[0]}"})
            total_score += 10
        else:
            score_details.append({"item": "检查是否在目录中创建了文件", "score": 0, "max_score": 10, "passed": False, "reason": "final_report 中没有找到文件"})
    else:
        score_details.append({"item": "检查是否在目录中创建了文件", "score": 0, "max_score": 10, "passed": False, "reason": "final_report 目录不存在，无法查找文件"})

    # 3. 大模型语义验证：检查异常用量患者 ID
    if file_found and report_content.strip():
        prompt_ids = (
            "Does the document clearly state that the flagged Patient IDs for Amoxicillin "
            "(those with a dose > 200mg) are exactly 'P-114' and 'P-902', and NO OTHERS are flagged?"
        )
        if llm_judge_content(prompt_ids, report_content):
            score_details.append({"item": "检查是否正确找出大剂量患者ID (P-114, P-902)", "score": 35, "max_score": 35, "passed": True, "reason": "大模型判定患者 ID 提取完全正确无多余"})
            total_score += 35
        else:
            score_details.append({"item": "检查是否正确找出大剂量患者ID (P-114, P-902)", "score": 0, "max_score": 35, "passed": False, "reason": "大模型判定患者 ID 提取有误或包含幻觉数据"})
    else:
        score_details.append({"item": "检查是否正确找出大剂量患者ID (P-114, P-902)", "score": 0, "max_score": 35, "passed": False, "reason": "缺少文件或内容为空"})

    # 4. 大模型语义验证：检查每种药物的总发药数量
    if file_found and report_content.strip():
        prompt_counts = (
            "Does the document report the following exact total pill quantities dispensed "
            "across all medications without hallucinating extra medications?\n"
            "- Lisinopril: 90\n"
            "- Amoxicillin: 74\n"
            "- Metformin: 120\n"
            "- Atorvastatin: 30\n"
            "- Ibuprofen: 100\n"
            "If any count is wrong, missing, or if additional medications are listed, answer NO."
        )
        if llm_judge_content(prompt_counts, report_content):
            score_details.append({"item": "检查各药物发放总数是否完全正确", "score": 35, "max_score": 35, "passed": True, "reason": "大模型判定所有药物汇总数字完全准确"})
            total_score += 35
        else:
            score_details.append({"item": "检查各药物发放总数是否完全正确", "score": 0, "max_score": 35, "passed": False, "reason": "大模型判定药物统计数据错误或缺失"})
    else:
        score_details.append({"item": "检查各药物发放总数是否完全正确", "score": 0, "max_score": 35, "passed": False, "reason": "缺少文件或内容为空"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace_path)
