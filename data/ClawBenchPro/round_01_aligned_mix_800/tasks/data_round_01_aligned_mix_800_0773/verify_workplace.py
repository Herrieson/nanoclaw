import os
import sys
import json
import pandas as pd
import httpx
from openai import OpenAI

# 配置常量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端
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
                {"role": "system", "content": "You are a strict academic integrity investigator. Answer ONLY with 'YES' or 'NO'."},
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
    report_dir = os.path.join(workspace, "investigation_report")
    score_details = []
    
    # 1. 目录结构检查 (10分)
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        score_details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "investigation_report 目录已创建"})
    else:
        score_details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 investigation_report 目录"})
        # 如果目录不存在，后续检查很难进行，初始化空分
        final_score = sum(d["score"] for d in score_details)
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": final_score, "details": score_details}, f)
        return

    # 2. 识别可疑支出清单 (40分)
    # 标准违规项：
    # EXP-003: Dr. Malicious (不在名单) 且 无产出 (UNK-999)
    # EXP-004: Dr. Chen (在名单) 但 金额>5000 且 无产出 (EDU-2023-C)
    # EXP-007: Dr. Aris (在名单) 但 金额>5000 且 无产出 (EDU-2023-E)
    suspicious_ids = {"EXP-003", "EXP-004", "EXP-007"}
    found_suspicious_files = [f for f in os.listdir(report_dir) if "list" in f.lower() or "suspicious" in f.lower()]
    
    if found_suspicious_files:
        suspicious_file_path = os.path.join(report_dir, found_suspicious_files[0])
        try:
            content = open(suspicious_file_path, "r", encoding="utf-8").read()
            detected_ids = [id for id in suspicious_ids if id in content]
            incorrect_ids = [id for id in ["EXP-001", "EXP-002", "EXP-005", "EXP-006"] if id in content]
            
            score_item = 0
            if "EXP-003" in detected_ids: score_item += 15 # 最严重的违规（名单外）
            if "EXP-004" in detected_ids: score_item += 10 # 大额无产出
            if "EXP-007" in detected_ids: score_item += 15 # 大额无产出
            score_item = max(0, score_item - len(incorrect_ids) * 10) # 错误识别扣分
            
            score_details.append({"item": "可疑支出识别准确度", "score": score_item, "max_score": 40, "passed": score_item >= 30, "reason": f"识别到 ID: {detected_ids}"})
        except Exception:
            score_details.append({"item": "可疑支出识别准确度", "score": 0, "max_score": 40, "passed": False, "reason": "无法解析清单文件"})
    else:
        score_details.append({"item": "可疑支出识别准确度", "score": 0, "max_score": 40, "passed": False, "reason": "未找到支出清单文件"})

    # 3. 统计摘要检查 (20分)
    summary_files = [f for f in os.listdir(report_dir) if "summary" in f.lower() or "abstract" in f.lower() or "report" in f.lower() and f not in found_suspicious_files]
    if summary_files:
        summary_path = os.path.join(report_dir, summary_files[0])
        content = open(summary_path, "r", encoding="utf-8").read()
        # 验证总金额统计：8000 + 6000 + 5200 = 19200
        has_total = "19200" in content
        has_count = "3" in content or "三" in content
        
        score_sum = 0
        if has_total: score_sum += 10
        if has_count: score_sum += 10
        score_details.append({"item": "统计摘要数据准确性", "score": score_sum, "max_score": 20, "passed": score_sum == 20, "reason": f"金额匹配: {has_total}, 数量匹配: {has_count}"})
    else:
        score_details.append({"item": "统计摘要数据准确性", "score": 0, "max_score": 20, "passed": False, "reason": "未找到摘要统计文件"})

    # 4. LLM 报告专业度与逻辑验证 (30分)
    all_report_content = ""
    for root, dirs, files in os.walk(report_dir):
        for f in files:
            all_report_content += open(os.path.join(root, f), "r", encoding="utf-8").read() + "\n"
    
    if all_report_content:
        prompt = "The report should clearly state that Dr. Malicious is not on the white list and explain why EXP-004/EXP-007 are suspicious (amount > 5000 and no publication). Is this professional and accurate?"
        is_professional = llm_judge_content(prompt, all_report_content)
        score_llm = 30 if is_professional else 10
        score_details.append({"item": "LLM 报告专业度评价", "score": score_llm, "max_score": 30, "passed": is_professional, "reason": "评价报告是否解释了违规逻辑及身份合规性"})
    else:
        score_details.append({"item": "LLM 报告专业度评价", "score": 0, "max_score": 30, "passed": False, "reason": "无报告内容可供评估"})

    total_score = sum(d["score"] for d in score_details)
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)

if __name__ == "__main__":
    verify()
