import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型非结构化文本验证器"""
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
    details = []
    total_score = 0
    
    final_report_dir = os.path.join(workspace, "final_report")
    
    # Check 1: 目录是否存在 (10 points)
    if os.path.isdir(final_report_dir):
        total_score += 10
        details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 final_report 存在"})
    else:
        details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 final_report 不存在"})
        
    # Check 2: 目录内是否包含报告文件 (10 points)
    report_content = ""
    if os.path.isdir(final_report_dir):
        files = os.listdir(final_report_dir)
        files = [f for f in files if os.path.isfile(os.path.join(final_report_dir, f))]
        if len(files) > 0:
            total_score += 10
            details.append({"item": "检查是否生成报告文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到报告文件 {files[0]}"})
            try:
                with open(os.path.join(final_report_dir, files[0]), 'r', encoding='utf-8', errors='ignore') as f:
                    report_content = f.read()
            except Exception:
                pass
        else:
            details.append({"item": "检查是否生成报告文件", "score": 0, "max_score": 10, "passed": False, "reason": "final_report 目录下无文件"})
    else:
        details.append({"item": "检查是否生成报告文件", "score": 0, "max_score": 10, "passed": False, "reason": "缺少结果目录"})

    # Check 3 & 4: Require report content to proceed
    if report_content:
        # Check 3: LLM 检查 DANGEROUS 异常识别是否精准 (40 points)
        # Truth: P-114 (Amoxicillin 250), P-902 (Amoxicillin 500)
        prompt_danger = (
            "Examine the following report. Does it explicitly identify ONLY the patients 'P-114' and 'P-902' "
            "(or similar exact references to these two IDs) as having DANGEROUS dosages? "
            "If it misses either P-114 or P-902, or if it incorrectly flags other patients (e.g., P-001, P-002, P-005, P-008, XYZ-99) as dangerous, you must answer NO."
        )
        if llm_judge_content(prompt_danger, report_content):
            total_score += 40
            details.append({"item": "检查是否精准识别所有 DANGEROUS 病人ID", "score": 40, "max_score": 40, "passed": True, "reason": "大模型判定报告准确提取了 P-114 和 P-902 作为危险剂量"})
        else:
            details.append({"item": "检查是否精准识别所有 DANGEROUS 病人ID", "score": 0, "max_score": 40, "passed": False, "reason": "大模型判定报告未提取出正确的危险ID，或存在多提、错提的情况"})

        # Check 4: LLM 检查多源文件的药品数量总计是否正确 (40 points)
        # Truth values: Lisinopril:90, Amoxicillin:74, Metformin:120, Atorvastatin:30, Ibuprofen:100
        prompt_totals = (
            "Examine the following report. Does it state the exact aggregate pill counts (Quantity Dispensed) "
            "for the following medications across all files: \n"
            "- Lisinopril: 90\n"
            "- Amoxicillin: 74\n"
            "- Metformin: 120\n"
            "- Atorvastatin: 30\n"
            "- Ibuprofen: 100\n"
            "All five values must be present and exactly match these numbers. If any number is wrong or missing, answer NO."
        )
        if llm_judge_content(prompt_totals, report_content):
            total_score += 40
            details.append({"item": "检查全量数据药品计数聚合", "score": 40, "max_score": 40, "passed": True, "reason": "大模型判定药品汇总计数完全正确"})
        else:
            details.append({"item": "检查全量数据药品计数聚合", "score": 0, "max_score": 40, "passed": False, "reason": "大模型判定报告中的药品计数存在缺失或计算错误"})
            
    else:
        details.append({"item": "检查是否精准识别所有 DANGEROUS 病人ID", "score": 0, "max_score": 40, "passed": False, "reason": "未找到报告内容"})
        details.append({"item": "检查全量数据药品计数聚合", "score": 0, "max_score": 40, "passed": False, "reason": "未找到报告内容"})

    score_result = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(score_result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace_path)
