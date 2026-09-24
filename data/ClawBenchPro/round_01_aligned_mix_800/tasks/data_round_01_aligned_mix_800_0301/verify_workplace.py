import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------------------------------------------------------
# 核心计算逻辑对照：
# 捐赠收入：
# TXN-001: $500 (Settled) -> +500
# TXN-002: $200 (Bounced) -> 0
# Carlos: $300 (Cash) -> +300
# Mateo: Cancelled -> 0
# TXN-003: $1000 (Settled) -> +1000
# Luis: Cancelled -> 0
# TXN-004: $2000 (Settled) -> +2000
# TXN-005: $100 Bounced -> 0
# 总收入 = 500 + 300 + 1000 + 2000 = $3800
#
# 支出费用：
# mariachi_invoice.pdf: $800
# gastos.log (Tamales): $350
# gastos.log (Permit): $50 (EXCLUDE - paid by church)
# 总支出 = 800 + 350 = $1150
#
# 最终余额 = 3800 - 1150 = $2650
# ----------------------------------------------------------------

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
                {"role": "system", "content": "You are a strict financial report auditor. Answer ONLY with 'YES' or 'NO'."},
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
    report_dir = os.path.join(workspace, "final_report")
    score = 0
    details = []

    # 1. 目录与基本文件检查 (10分)
    if os.path.exists(report_dir):
        score += 5
        details.append({"item": "检查报告目录", "score": 5, "max_score": 5, "passed": True, "reason": "final_report 目录已创建"})
    else:
        details.append({"item": "检查报告目录", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 final_report 目录"})

    report_files = [f for f in os.listdir(report_dir) if f.endswith(".txt") or f.endswith(".md")] if os.path.exists(report_dir) else []
    if report_files:
        score += 5
        report_path = os.path.join(report_dir, report_files[0])
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        details.append({"item": "检查报告文件是否存在", "score": 5, "max_score": 5, "passed": True, "reason": f"找到报告: {report_files[0]}"})
    else:
        details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "未找到报告文件"})
        return score, details # 无法进行后续检查

    # 2. 数值准确性检查 - 硬性指标 (50分)
    # 正确值: 收入 3800, 支出 1150, 余额 2650
    target_balance = "2650"
    target_income = "3800"
    target_expense = "1150"

    # 检查余额 (30分)
    if target_balance in content:
        score += 30
        details.append({"item": "最终余额计算准确性", "score": 30, "max_score": 30, "passed": True, "reason": f"报告包含正确余额 ${target_balance}"})
    else:
        details.append({"item": "最终余额计算准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"报告未包含正确余额 ${target_balance}"})

    # 检查收入与支出明细 (20分)
    if target_income in content and target_expense in content:
        score += 20
        details.append({"item": "总收支明细准确性", "score": 20, "max_score": 20, "passed": True, "reason": "报告包含正确总收入和总支出"})
    else:
        details.append({"item": "总收支明细准确性", "score": 0, "max_score": 20, "passed": False, "reason": "总收入或总支出数值错误"})

    # 3. 排除逻辑检查 (20分)
    # 检查是否错误地扣除了教堂支付的 $50 许可费 (如果余额是 2600 则代表多扣了)
    if "2600" in content and "2650" not in content:
        details.append({"item": "陷阱排除逻辑 (Permit Fee)", "score": 0, "max_score": 10, "passed": False, "reason": "错误地扣除了教堂直接支付的 $50 许可费"})
    else:
        score += 10
        details.append({"item": "陷阱排除逻辑 (Permit Fee)", "score": 10, "max_score": 10, "passed": True, "reason": "正确处理了无需扣除的许可费"})

    # 检查是否包含了被退票或取消的捐款
    if "200" in content or "100" in content or "150" in content:
         # 这几个数字如果以收入形式出现则是错误的
         is_error = llm_judge_content("Does this report incorrectly count $200, $100, or $150 as valid incoming donations? (If they are listed as 'Bounced' or 'Cancelled' it is fine)", content)
         if is_error:
             details.append({"item": "无效捐款过滤", "score": 0, "max_score": 10, "passed": False, "reason": "报告包含了已退票或已取消的捐款"})
         else:
             score += 10
             details.append({"item": "无效捐款过滤", "score": 10, "max_score": 10, "passed": True, "reason": "报告正确排除了无效捐款"})
    else:
        score += 10
        details.append({"item": "无效捐款过滤", "score": 10, "max_score": 10, "passed": True, "reason": "报告未包含明显的无效金额"})

    # 4. LLM 语义与易读性检查 (20分)
    # 语气是否适合工人向牧师汇报 (简明扼要)
    is_readable = llm_judge_content("Is this report written in a simple, clear manner suitable for a construction worker to present to a Pastor? (No code snippets, no JSON, just clear numbers and text)", content)
    if is_readable:
        score += 10
        details.append({"item": "报告易读性 (符合用户背景)", "score": 10, "max_score": 10, "passed": True, "reason": "报告语言通俗易懂，符合人物设定"})
    else:
        details.append({"item": "报告易读性 (符合用户背景)", "score": 0, "max_score": 10, "passed": False, "reason": "报告包含代码片段或格式过于极客，不符合设定"})

    # 是否提及了 Mariachi 支出的来源 (证明读取了 PDF)
    mentions_mariachi = llm_judge_content("Does the report explicitly mention the $800 expense for the Mariachi band/invoice?", content)
    if mentions_mariachi:
        score += 10
        details.append({"item": "关键信息完整性 (PDF 解析)", "score": 10, "max_score": 10, "passed": True, "reason": "报告包含了从 PDF 中提取的 Mariachi 支出"})
    else:
        details.append({"item": "关键信息完整性 (PDF 解析)", "score": 0, "max_score": 10, "passed": False, "reason": "报告遗漏了关键的 Mariachi 乐队支出"})

    return min(score, 100), details

if __name__ == "__main__":
    final_score, score_details = verify()
    output = {
        "total_score": int(final_score),
        "details": score_details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
