import os
import sys
import json
import re
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
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # 1. Check Directory Existence (10 points)
    dir_exists = os.path.isdir(deliverables_dir)
    if dir_exists:
        score_details.append({"item": "Deliverables目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建了 deliverables 目录。"})
        total_score += 10
    else:
        score_details.append({"item": "Deliverables目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录。"})
        
    # Read all content from the deliverables directory
    report_content = ""
    if dir_exists:
        for root, _, files in os.walk(deliverables_dir):
            for file in files:
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        report_content += f.read() + "\n"
                except Exception:
                    pass

    # 2. Check Report File Exists and is not empty (10 points)
    if dir_exists and len(report_content.strip()) > 10:
        score_details.append({"item": "报告内容非空", "score": 10, "max_score": 10, "passed": True, "reason": "已在报告中写入内容。"})
        total_score += 10
    else:
        score_details.append({"item": "报告内容非空", "score": 0, "max_score": 10, "passed": False, "reason": "报告文件不存在或内容为空。"})
        report_content = "" # Reset for subsequent checks to fail safely

    # 3. Exact Number Extraction for Total Expenses (30 points)
    # The correct amount is exactly 1600.75 (450 + 210.5 + 875 + 65.25)
    # We use regex to avoid fuzzy matching on structured numbers
    expense_match = re.search(r'1[ ,]?600\.75', report_content)
    if expense_match:
        score_details.append({"item": "精准计算安全设备支出", "score": 30, "max_score": 30, "passed": True, "reason": "准确提取并计算了费用总和 1600.75。"})
        total_score += 30
    else:
        score_details.append({"item": "精准计算安全设备支出", "score": 0, "max_score": 30, "passed": False, "reason": "未能得出正确的开销总计 1600.75，可能遗漏、计算错误或混入了诱饵数据。"})

    # 4. LLM Semantic Check for Violations (40 points, 10 per specific violation)
    violations = [
        ("Exposed high-voltage wiring", "Does the text mention exposed high-voltage wiring (in Section 4)?"),
        ("No fire extinguisher", "Does the text mention a missing fire extinguisher at the welding station?"),
        ("Uncertified forklift operation", "Does the text mention workers operating a forklift without certification?"),
        ("Missing scaffolding toe-boards", "Does the text mention scaffolding missing toe-boards (on the North face)?")
    ]
    
    violation_score = 0
    if report_content:
        for name, prompt in violations:
            passed = llm_judge_content(prompt, report_content)
            if passed:
                violation_score += 10
                score_details.append({"item": f"违规项提取: {name}", "score": 10, "max_score": 10, "passed": True, "reason": f"成功提取了违规记录：{name}。"})
            else:
                score_details.append({"item": f"违规项提取: {name}", "score": 0, "max_score": 10, "passed": False, "reason": f"未能提取到关键违规记录：{name}。"})
    else:
        for name, _ in violations:
            score_details.append({"item": f"违规项提取: {name}", "score": 0, "max_score": 10, "passed": False, "reason": "报告为空，无法提取。"})
            
    total_score += violation_score

    # 5. LLM Negative Check - Hallucination/Decoy filter (10 points)
    # Ensure they didn't include art supplies or decoys
    if report_content:
        hallucination_prompt = "Does the text mention ANY art supplies (e.g., Oil Paint, Marble Slab, Chisels, Canvas, Turpentine) or expenses unrelated to safety?"
        has_hallucination = llm_judge_content(hallucination_prompt, report_content)
        if not has_hallucination:
            score_details.append({"item": "剔除干扰数据", "score": 10, "max_score": 10, "passed": True, "reason": "未发现无关的美术用品或诱饵数据，数据清洗严谨。"})
            total_score += 10
        else:
            score_details.append({"item": "剔除干扰数据", "score": 0, "max_score": 10, "passed": False, "reason": "报告中混入了美术用品等诱饵数据，未按 CATEGORY 严格过滤。"})
    else:
        score_details.append({"item": "剔除干扰数据", "score": 0, "max_score": 10, "passed": False, "reason": "报告为空。"})

    # Write final score
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
