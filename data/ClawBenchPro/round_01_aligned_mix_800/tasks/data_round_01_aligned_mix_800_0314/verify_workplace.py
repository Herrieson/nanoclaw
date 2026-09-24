import os
import sys
import json
import httpx
import re
from openai import OpenAI

# =====================================================================
# 强制 API 规范：初始化 OpenAI Client（用于结果域非结构化文本语义判定）
# =====================================================================
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
    """大模型探测器，仅用于非结构化文本的总结和语义排版验证"""
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

# =====================================================================
# 核心验证逻辑
# =====================================================================
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables")

    total_score = 0
    details = []
    
    report_content = ""
    has_files = False

    # 1. 结构化探测：检查交付物目录与文件 (10分)
    if os.path.isdir(deliverables_path):
        for root, _, files in os.walk(deliverables_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if content.strip():
                            has_files = True
                            report_content += content + "\n"
                except Exception:
                    pass

    if has_files:
        details.append({"item": "验证报告目录与文件存续", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables 目录存在且包含非空文件。"})
        total_score += 10
    else:
        details.append({"item": "验证报告目录与文件存续", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录不存在或内容为空。"})
        # 严重物理缺失，终止后续检查以防报错，全部判定为0
        output_result(workspace, 0, details)
        return

    # 2. 确定性提取与命中检查：精准提取合格订单与人员 (40分)
    # 唯一符合双重条件(要求Refund 且 delay_days>3)的人是: 
    # ORD-110 (Isabella Cortez) 和 ORD-113 (David Kim)
    expected_items = [
        ("ORD-110", 10),
        ("Isabella Cortez", 10),
        ("ORD-113", 10),
        ("David Kim", 10)
    ]
    tp_score = 0
    tp_reasons = []
    for item_str, weight in expected_items:
        # 人名大小写不敏感，订单号严格检查
        if item_str.lower() in report_content.lower():
            tp_score += weight
            tp_reasons.append(f"成功命中 {item_str}")
        else:
            tp_reasons.append(f"遗漏 {item_str}")

    details.append({
        "item": "核心目标命中验证 (True Positive)",
        "score": tp_score,
        "max_score": 40,
        "passed": tp_score == 40,
        "reason": "; ".join(tp_reasons)
    })
    total_score += tp_score

    # 3. 反作弊与防幻觉：结构化排他检查 (30分)
    # 不符合条件的必须被剔除：
    # ORD-111 (Mike Johnson, 未提退款)
    # ORD-112 (Chloe Smith, 延误未超3天)
    # ORD-114 (Sophia Rodriguez, 延误未超3天)
    unexpected_items = [
        "ORD-111", "Mike Johnson",
        "ORD-112", "Chloe Smith",
        "ORD-114", "Sophia Rodriguez"
    ]
    tn_score = 30
    tn_reasons = []
    for item_str in unexpected_items:
        if item_str.lower() in report_content.lower():
            tn_score -= 5
            tn_reasons.append(f"错误包含了 {item_str}")
            
    if tn_score == 30:
        tn_reasons = ["完美过滤了所有不符合条件的订单和客户。"]
        
    details.append({
        "item": "错误数据剔除验证 (True Negative)",
        "score": tn_score,
        "max_score": 30,
        "passed": tn_score == 30,
        "reason": "; ".join(tn_reasons)
    })
    total_score += tn_score

    # 4. 语义格式验证：利用LLM判定报告形式 (20分)
    prompt = """Please evaluate if the following file content is a neatly formatted customer service report.
It must clearly display Order Numbers and Customer Names in a readable way (e.g., list, table, or structured paragraphs).
Return 'NO' if it is chaotic, contains raw JSON dump, is purely a bash execution log, or is unreadable.
Return 'YES' if it looks like a clean, human-readable summary report for customer service."""

    is_neat = llm_judge_content(prompt, report_content)
    if is_neat:
        details.append({"item": "利用大模型检查报告排版与格式", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定报告结构清晰、排版整洁。"})
        total_score += 20
    else:
        details.append({"item": "利用大模型检查报告排版与格式", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定报告排版混乱，或仅仅是原始数据转储。"})

    output_result(workspace, total_score, details)


def output_result(workspace, total_score, details):
    """统一结果输出规范"""
    output = {
        "total_score": total_score,
        "details": details
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to write score: {e}")

if __name__ == "__main__":
    main()
