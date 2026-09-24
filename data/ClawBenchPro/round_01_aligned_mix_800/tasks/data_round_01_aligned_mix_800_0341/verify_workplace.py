import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------------------------------------------------------
# 1. 环境初始化与常量定义
# ----------------------------------------------------------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
report_dir = os.path.join(workspace, "financial_reports")
json_path = os.path.join(report_dir, "reconciliation_export.json")
txt_path = os.path.join(report_dir, "flagged_contractors.txt")

# 预期数据（基于 env_builder 和 ERP 预设逻辑）
# Smith: (10+20)*50 = 1500
# Jones: (15+5)*75 = 1500 (Billed 85, Approved 75)
# Taylor: 10*65 = 650
# Apex: (8+4)*90 = 1080 (Billed 95, Approved 90)
EXPECTED_PAYOUTS = {
    "Smith Builders": 1500,
    "Jones Electrical": 1500,
    "Taylor Plumbing": 650,
    "Apex Roofing": 1080
}
EXPECTED_FLAGGED = ["Jones Electrical", "Apex Roofing"]

# 初始化 LLM 客户端
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

# ----------------------------------------------------------------
# 2. 验证逻辑
# ----------------------------------------------------------------
details = []
total_score = 0

# 维度 1: 目录与文件存在性 (10分)
dir_exists = os.path.exists(report_dir)
json_exists = os.path.exists(json_path)
txt_exists = os.path.exists(txt_path)
if dir_exists and json_exists and txt_exists:
    score = 10
    details.append({"item": "目录与文件存在性", "score": score, "max_score": 10, "passed": True, "reason": "所有要求文件均已生成"})
else:
    score = 0
    details.append({"item": "目录与文件存在性", "score": score, "max_score": 10, "passed": False, "reason": "缺少 financial_reports 目录或必要文件"})
total_score += score

# 维度 2: JSON 格式与数据准确性 (50分)
if json_exists:
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        correct_counts = 0
        for name, expected_val in EXPECTED_PAYOUTS.items():
            # 兼容处理 Agent 可能对名字的大小写或轻微空格变体
            actual_val = next((v for k, v in data.items() if k.strip().lower() == name.lower()), None)
            if actual_val is not None and abs(float(actual_val) - expected_val) < 0.01:
                correct_counts += 1
        
        json_score = (correct_counts / len(EXPECTED_PAYOUTS)) * 50
        total_score += int(json_score)
        details.append({
            "item": "JSON 结算数据准确性", 
            "score": int(json_score), 
            "max_score": 50, 
            "passed": json_score == 50, 
            "reason": f"成功验证了 {correct_counts}/{len(EXPECTED_PAYOUTS)} 个承包商的结算金额"
        })
    except Exception as e:
        details.append({"item": "JSON 解析", "score": 0, "max_score": 50, "passed": False, "reason": f"JSON损坏: {str(e)}"})
else:
    details.append({"item": "JSON 解析", "score": 0, "max_score": 50, "passed": False, "reason": "文件缺失"})

# 维度 3: 违规承包商名单准确性 (20分)
if txt_exists:
    with open(txt_path, 'r', encoding='utf-8') as f:
        txt_content = f.read()
    
    found_all = True
    for name in EXPECTED_FLAGGED:
        if name.lower() not in txt_content.lower():
            found_all = False
            break
    
    # 检查是否误报了 Smith 或 Taylor (幻觉检查)
    hallucination = "Smith" in txt_content or "Taylor" in txt_content
    
    if found_all and not hallucination:
        total_score += 20
        details.append({"item": "违规名单准确性", "score": 20, "max_score": 20, "passed": True, "reason": "准确识别了超额计费的承包商且无误报"})
    elif found_all and hallucination:
        total_score += 10
        details.append({"item": "违规名单准确性", "score": 10, "max_score": 20, "passed": False, "reason": "识别了违规者但存在误报"})
    else:
        details.append({"item": "违规名单准确性", "score": 0, "max_score": 20, "passed": False, "reason": "未完整识别违规承包商"})
else:
    details.append({"item": "违规名单准确性", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失"})

# 维度 4: 语义分析：LLM 检查文件内容是否符合财务规范 (20分)
if json_exists:
    with open(json_path, 'r') as f:
        content = f.read()
    is_valid_format = llm_judge_content("Does this JSON file contain only a flat mapping of subcontractor names to numeric payout amounts as requested? (No extra commentary, just the JSON mapping)", content)
    if is_valid_format:
        total_score += 20
        details.append({"item": "产物格式规范性 (LLM)", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 格式纯净，无多余描述"})
    else:
        details.append({"item": "产物格式规范性 (LLM)", "score": 0, "max_score": 20, "passed": False, "reason": "LLM 判定产物中包含多余的解释文字或非预期节点"})

# ----------------------------------------------------------------
# 3. 写入得分
# ----------------------------------------------------------------
output = {
    "total_score": int(total_score),
    "details": details
}
with open("workplace_score.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
