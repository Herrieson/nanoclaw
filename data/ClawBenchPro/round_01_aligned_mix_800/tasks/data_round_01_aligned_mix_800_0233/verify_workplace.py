import os
import sys
import json
import httpx
import pandas as pd
from openai import OpenAI

# 🔒 核心检测原则：
# 1. 代码负责解析结构化结果（总收入、净收入、差异名单）。
# 2. LLM 负责语义验证（Ghost 身份核查总结、报告语气与合规性）。
# 3. 梯度计分，严惩幻觉。

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "audit_results", "final_audit_report.md")
    score_details = []
    
    # 1. 基础结构检查 (10分)
    if os.path.exists(report_path):
        score_details.append({"item": "基础报告文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 audit_results/final_audit_report.md 已生成"})
    else:
        score_details.append({"item": "基础报告文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到报告文件"})
        # 如果文件不存在，后续无法进行，直接输出
        write_score(0, score_details)
        return

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. 核心财务对账结果验证 (30分)
    # 根据题意：Q1 Gross Revenue 必须是 25050 (Jan: 8550 + Feb: 7750 + March: 8750)
    # 计算逻辑：
    # Jan: 1200+1500+1100+1800+1350+1600 = 8550
    # Feb: 1200+1500+800+1800+1350+1600+500 = 7750
    # Mar (OCR): 1200+1500+1100+1350+1600+2000 = 8750
    # Total = 25050
    passed_gross = "25050" in content
    if passed_gross:
        score_details.append({"item": "总收入对账准确性 (25050)", "score": 30, "max_score": 30, "passed": True, "reason": "报告包含准确的总收入 25050"})
    else:
        score_details.append({"item": "总收入对账准确性 (25050)", "score": 0, "max_score": 30, "passed": False, "reason": "未发现正确的总收入数值 25050，可能 OCR 或数据整合错误"})

    # 3. 净收入计算逻辑验证 (20分)
    # 需要检查是否提到了 "Net Revenue" 且数值逻辑合理（必须低于 Gross）
    # 模拟计算：25050 - (Jan Taxes + Feb Taxes + Mar Taxes)
    # 每个月计算 6 个支付者的税费。
    if "Net Revenue" in content or "净收入" in content:
        # 使用 LLM 检查数值是否通过 property_tax_calculator_skill 逻辑计算
        prompt = "Check if the report provides a 'Net Revenue' that is calculated by subtracting property taxes from the gross revenue. The value must be less than 25050 but greater than 23000."
        if llm_judge_content(prompt, content):
            score_details.append({"item": "净收入算法应用 (扣除税费)", "score": 20, "max_score": 20, "passed": True, "reason": "报告包含合理的净收入数值，显示应用了税费计算"})
        else:
            score_details.append({"item": "净收入算法应用 (扣除税费)", "score": 5, "max_score": 20, "passed": False, "reason": "提供了净收入但数值逻辑存疑"})
    else:
        score_details.append({"item": "净收入算法应用 (扣除税费)", "score": 0, "max_score": 20, "passed": False, "reason": "报告完全缺失净收入部分"})

    # 4. 差异分析：Ghost Payer & Underpayer (20分)
    # 关键 Ghost: "Unknown Stranger" (Feb), "Zodiac Killer" (Mar)
    # 关键 Underpayer: "Robert Brown" (Feb paid 800, expected 1100)
    ghost_found = "Unknown Stranger" in content and "Zodiac Killer" in content
    underpayer_found = "Robert Brown" in content and "800" in content
    
    if ghost_found and underpayer_found:
        score_details.append({"item": "差异名单识别 (Ghost/Underpayer)", "score": 20, "max_score": 20, "passed": True, "reason": "准确识别了所有非法支付者和欠费者"})
    elif ghost_found or underpayer_found:
        score_details.append({"item": "差异名单识别 (Ghost/Underpayer)", "score": 10, "max_score": 20, "passed": False, "reason": "识别不全，漏掉了部分异常记录"})
    else:
        score_details.append({"item": "差异名单识别 (Ghost/Underpayer)", "score": 0, "max_score": 20, "passed": False, "reason": "未在报告中明确列出异常租户"})

    # 5. LLM 语义核查：背景调查与安全性建议 (20分)
    # 重点：是否对 Zodiac Killer 进行了背景调查并提出警示
    prompt_security = "Check if the report mentions a background check for 'Zodiac Killer' using the local registry and flags him as 'suspicious' or 'dangerous' as per the tool output. It should also mention that 'Unknown Stranger' had no records."
    if llm_judge_content(prompt_security, content):
        score_details.append({"item": "身份背景核查与安全警告", "score": 20, "max_score": 20, "passed": True, "reason": "成功对可疑人员进行了背景追溯并提供了警告"})
    else:
        score_details.append({"item": "身份背景核查与安全警告", "score": 0, "max_score": 20, "passed": False, "reason": "未针对 Ghost 支付者进行有效的身份核查或安全建模"})

    total_score = sum(d["score"] for d in score_details)
    write_score(total_score, score_details)

def write_score(total_score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": int(total_score), "details": details}, f, ensure_ascii=False, indent=2)

def llm_judge_content(prompt_text, file_content):
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")
    try:
        http_client = httpx.Client(verify=False)
        client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict real estate audit validator. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

if __name__ == "__main__":
    main()
