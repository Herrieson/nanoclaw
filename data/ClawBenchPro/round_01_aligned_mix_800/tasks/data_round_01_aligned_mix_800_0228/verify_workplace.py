import os
import sys
import json
import httpx
from openai import OpenAI

# Configuration for LLM
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize OpenAI client
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
    report_dir = os.path.join(workspace, "inventory_reports")
    details = []
    total_score = 0

    # Ground Truth Data
    # Batch_A: 
    #   Shea Butter (SB-101): 500 (Organic)
    #   Lye (LY-01): 100 (Pending) -> IGNORE
    #   Lavender Oil (LO-02): 50 (Organic)
    #   Coconut Oil (CO-44): 200 (Rejected) -> IGNORE
    #   Shea Butter (SB-102): 150 (Organic)
    # Batch_B (PDF):
    #   Rose Water (RW-102): 30 (Organic)
    #   Artificial Dye (AD-99): 500 (Rejected) -> IGNORE
    #   Lavender Oil (LO-05): 10 (Pending) -> IGNORE
    #
    # EXPECTED TOTALS:
    # Shea Butter: 500 + 150 = 650
    # Lavender Oil: 50 (Only LO-02 is organic, LO-05 is pending)
    # Rose Water: 30
    
    expected_values = {
        "Shea Butter": 650,
        "Lavender Oil": 50,
        "Rose Water": 30
    }

    # 1. Check Directory Existence (10 points)
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        files = [f for f in os.listdir(report_dir) if os.path.isfile(os.path.join(report_dir, f))]
        if files:
            details.append({"item": "检查结果目录与文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"找到目录及文件: {files[0]}"})
            report_file = os.path.join(report_dir, files[0])
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            details.append({"item": "检查结果目录与文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录存在但为空"})
            content = ""
    else:
        details.append({"item": "检查结果目录与文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "inventory_reports 目录缺失"})
        content = ""

    if content:
        # 2. Check for Distractor Exclusion (20 points)
        # Check if the guest list or napkin count (650) from guest_list.txt leaked into the report
        distractors = ["Sarah", "Bat Mitzvah", "Uncle David", "Aunt Rachel", "napkin"]
        leaked = [d for d in distractors if d.lower() in content.lower()]
        if not leaked:
            details.append({"item": "干扰项过滤（未包含嘉宾名单数据）", "score": 20, "max_score": 20, "passed": True, "reason": "未发现非业务数据泄露"})
        else:
            details.append({"item": "干扰项过滤（未包含嘉宾名单数据）", "score": 0, "max_score": 20, "passed": False, "reason": f"检测到干扰项泄露: {leaked}"})

        # 3. Calculation Accuracy - Shea Butter (25 points)
        if "650" in content:
            details.append({"item": "关键成分计算：Shea Butter (650 lbs)", "score": 25, "max_score": 25, "passed": True, "reason": "正确合并了 Batch_A 中的两个有机乳木果油批次"})
        else:
            details.append({"item": "关键成分计算：Shea Butter (650 lbs)", "score": 0, "max_score": 25, "passed": False, "reason": "未找到正确的乳木果油总重 650"})

        # 4. Filter Logic - Excluding Pending/Rejected (25 points)
        # Lavender Oil should be 50, NOT 60 (LO-05 is pending). Artificial Dye (500) and Coconut Oil (200) should be absent.
        prompt = f"Does the report correctly list Lavender Oil as 50 (ignoring the 10lbs pending batch) AND omit Artificial Dye (500lbs rejected) and Coconut Oil (200lbs rejected)?"
        if llm_judge_content(prompt, content):
            details.append({"item": "过滤逻辑验证：排除 Pending 和 Rejected 批次", "score": 25, "max_score": 25, "passed": True, "reason": "大模型确认报告正确过滤了非有机批次"})
        else:
            details.append({"item": "过滤逻辑验证：排除 Pending 和 Rejected 批次", "score": 0, "max_score": 25, "passed": False, "reason": "大模型判定过滤逻辑有误（可能误加了 Lavender Oil 或包含了染色剂）"})

        # 5. Multi-source integration - PDF content (20 points)
        if "30" in content and ("Rose Water" in content or "Rosewater" in content):
             details.append({"item": "多源数据整合：包含 PDF 扫描件中的 Rose Water", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析并整合了 PDF 中的有机成分数据"})
        else:
             details.append({"item": "多源数据整合：包含 PDF 扫描件中的 Rose Water", "score": 0, "max_score": 20, "passed": False, "reason": "未在报告中发现 PDF 扫描件提取的 Rose Water 30lbs 数据"})

    total_score = sum(d["score"] for d in details)
    
    output = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
