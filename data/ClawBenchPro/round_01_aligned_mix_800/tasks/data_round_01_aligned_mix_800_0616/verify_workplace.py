import os
import sys
import json
import csv
import httpx
import re
from openai import OpenAI

# 配置环境
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
                {"role": "system", "content": "You are a strict scientific data auditor. Answer ONLY with 'YES' or 'NO' and a brief reason after it."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        content = response.choices[0].message.content.strip().lower()
        return "yes" in content
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def calculate_expected():
    """计算预期的 top 3"""
    # SUBJ_001: (90/10) * (60/60) = 9.0
    # SUBJ_002: (100/5) * (50/60) = 16.666...
    # SUBJ_003: (85/15) * (70/60) = 6.611...
    # SUBJ_005: (110/4) * (45/60) = 20.625
    # SUBJ_006: (95/8) * (55/60) = 10.885...
    # SUBJ_009: (120/12) * (80/60) = 13.333...
    results = [
        ("SUBJ_005", 20.625),
        ("SUBJ_002", 16.666),
        ("SUBJ_009", 13.333)
    ]
    return results

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables")
    score_details = []
    total_score = 0

    # 1. 检查目录与文件存在性 (10分)
    item_1 = {"item": "检查交付物目录与报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if os.path.exists(deliverables_path):
        files = os.listdir(deliverables_path)
        if len(files) > 0:
            item_1["score"] = 10
            item_1["passed"] = True
            item_1["reason"] = f"发现文件: {files}"
        else:
            item_1["reason"] = "deliverables 目录为空"
    else:
        item_1["reason"] = "deliverables 目录未创建"
    score_details.append(item_1)

    # 2. 检查数据清洗逻辑 (30分)
    # 逻辑：检查报告是否包含了被排除的坏数据（SUBJ_004, 007, 008, 010）
    item_2 = {"item": "检查数据清洗（排除无效记录）", "score": 0, "max_score": 30, "passed": False, "reason": ""}
    report_content = ""
    if item_1["passed"]:
        report_file = os.path.join(deliverables_path, os.listdir(deliverables_path)[0])
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        invalid_ids = ["SUBJ_004", "SUBJ_007", "SUBJ_008", "SUBJ_010"]
        found_invalid = [uid for uid in invalid_ids if uid in report_content]
        if not found_invalid:
            item_2["score"] = 30
            item_2["passed"] = True
            item_2["reason"] = "成功剔除了所有负值、缺失值和NaN数据。"
        else:
            item_2["score"] = max(0, 30 - len(found_invalid) * 10)
            item_2["reason"] = f"报告中包含了错误的无效记录: {found_invalid}"
    score_details.append(item_2)

    # 3. 检查计算准确性 (40分)
    # 逻辑：检查 Top 3 的 ID 是否正确，且数值是否接近
    item_3 = {"item": "检查 MEQ 计算准确度与排名", "score": 0, "max_score": 40, "passed": False, "reason": ""}
    if report_content:
        expected = calculate_expected()
        correct_count = 0
        for uid, val in expected:
            # 检查 ID 存在
            if uid in report_content:
                # 使用正则查找该 ID 附近的数值
                match = re.search(rf"{uid}.*?(\d+\.?\d*)", report_content)
                if match:
                    reported_val = float(match.group(1))
                    if abs(reported_val - val) < 0.5: # 允许舍入误差
                        correct_count += 1
        
        item_3["score"] = int((correct_count / 3) * 40)
        if correct_count == 3:
            item_3["passed"] = True
            item_3["reason"] = "前三名 Subject ID 及其 MEQ 分值均计算正确。"
        else:
            item_3["reason"] = f"前三名中仅匹配成功 {correct_count} 个。需包含 SUBJ_005, SUBJ_002, SUBJ_009。"
    score_details.append(item_3)

    # 4. LLM 语义检查 - 报告可读性 (20分)
    item_4 = {"item": "利用大模型检查报告专业性与完整性", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    if report_content:
        prompt = "Check if the report clearly lists the Top 3 Subject IDs and their Metabolic Efficiency Quotients (MEQ). The report should be easy for a researcher to copy-paste into a presentation."
        if llm_judge_content(prompt, report_content):
            item_4["score"] = 20
            item_4["passed"] = True
            item_4["reason"] = "报告格式清晰，符合科研展示需求。"
        else:
            item_4["reason"] = "报告内容混乱或未明确标示 Top 3。"
    score_details.append(item_4)

    # 汇总
    total_score = sum(d["score"] for d in score_details)
    output = {"total_score": total_score, "details": score_details}
    
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
