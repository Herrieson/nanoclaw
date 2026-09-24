import os
import sys
import json
import pandas as pd
import httpx
from openai import OpenAI

# --- Configuration ---
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
                {"role": "system", "content": "You are a strict financial auditor. Answer ONLY with 'YES' or 'NO'."},
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
    score = 0
    details = []

    # Target directory and expected file
    audit_dir = os.path.join(workspace, "audit_results")
    
    # 1. Directory Structure (10 points)
    if os.path.exists(audit_dir) and os.path.isdir(audit_dir):
        score += 10
        details.append({"item": "目录结构检查", "score": 10, "max_score": 10, "passed": True, "reason": "audit_results 目录已创建"})
    else:
        details.append({"item": "目录结构检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 audit_results 目录"})
        # Write results early if critical path is missing
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # Find the report file (allow common extensions)
    report_file = None
    for f in os.listdir(audit_dir):
        if "summary" in f.lower() or "report" in f.lower() or "audit" in f.lower():
            report_file = os.path.join(audit_dir, f)
            break
    
    if not report_file:
        details.append({"item": "报告文件存在性", "score": 0, "max_score": 10, "passed": False, "reason": "在 audit_results 中未找到明显的总结报告文件"})
    else:
        score += 10
        details.append({"item": "报告文件存在性", "score": 10, "max_score": 10, "passed": True, "reason": f"找到报告文件: {os.path.basename(report_file)}"})

    # 2. Data Accuracy - Ground Truth Calculation
    # Expected Revenue: (1200+1500+1100+1800+1350+1600) * 3 = 8550 * 3 = 25650
    # Actual Revenue: 
    # M1: 8550
    # M2: 1200+1500+800+1800+1350+1600+500 = 8750
    # M3: 1200+1500+1100+1350+1600+2000 = 8750
    # Total Actual: 8550 + 8750 + 8750 = 26050
    # Underpayers: Robert Brown (M2), Emily Davis (M3 missed)
    # Ghost Payers: Unknown Stranger, Zodiac Killer

    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check Total Revenue (30 points)
        if "26050" in content:
            score += 30
            details.append({"item": "实收总额计算", "score": 30, "max_score": 30, "passed": True, "reason": "正确识别出实际总收入为 26050"})
        elif "25550" in content or "24050" in content:
            score += 15
            details.append({"item": "实收总额计算", "score": 15, "max_score": 30, "passed": False, "reason": "识别出部分金额但计算不完整"})
        else:
            details.append({"item": "实收总额计算", "score": 0, "max_score": 30, "passed": False, "reason": "未能正确计算实收总额 26050"})

        # Check Specific Identification (20 points)
        ghost_passed = "Unknown Stranger" in content and "Zodiac Killer" in content
        if ghost_passed:
            score += 20
            details.append({"item": "Ghost Payer 识别", "score": 20, "max_score": 20, "passed": True, "reason": "准确识别出两位编外付款人员"})
        else:
            details.append({"item": "Ghost Payer 识别", "score": 0, "max_score": 20, "passed": False, "reason": "未能完整识别 Unknown Stranger 和 Zodiac Killer"})

        # Check Delinquency/Underpayment Identification (15 points)
        underpay_passed = "Robert Brown" in content and "Emily Davis" in content
        if underpay_passed:
            score += 15
            details.append({"item": "欠缴/少缴识别", "score": 15, "max_score": 15, "passed": True, "reason": "准确识别出 Robert Brown 少缴和 Emily Davis 漏缴"})
        else:
            details.append({"item": "欠缴/少缴识别", "score": 0, "max_score": 15, "passed": False, "reason": "未能完整识别异常缴费租户"})

        # 3. LLM Audit - Professionalism and Structure (15 points)
        prompt = "Assess if this report is professionally structured for an auditor. It must clearly list discrepancies (underpayments and ghost payers) and provide a financial totals summary. Does it meet these criteria?"
        if llm_judge_content(prompt, content):
            score += 15
            details.append({"item": "报告专业度 (LLM)", "score": 15, "max_score": 15, "passed": True, "reason": "大模型判定报告结构清晰、专业"})
        else:
            details.append({"item": "报告专业度 (LLM)", "score": 0, "max_score": 15, "passed": False, "reason": "报告结构混乱或关键分类不明确"})

    except Exception as e:
        details.append({"item": "内容解析错误", "score": 0, "max_score": 65, "passed": False, "reason": str(e)})

    # Final Score Output
    final_data = {
        "total_score": min(100, score),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
