import os
import sys
import json
import httpx
from openai import OpenAI

# 配置常量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化 LLM 客户端
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """用于验证非结构化报告的质量和语气"""
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
    score = 0
    details = []

    # 预期结果数据
    # 计算过程: 32人 / 4人基准 = 8倍
    # Tortillas: 12 * 8 = 96 | Chicken: 2.0 * 8 = 16.0 | Cheese: 16 * 8 = 128 | Sauce: 1.0 * 8 = 8
    # 缺口: 96-26=70, 16-4.5=11.5, 128-28=100, 8-3=5
    EXPECTED_PEOPLE = 32
    EXPECTED_PURCHASE = {
        "tortillas": 70,
        "chicken_lbs": 11.5,
        "cheese_oz": 100.0,
        "sauce_cans": 5.0
    }

    deliverables_path = os.path.join(workspace, "deliverables")
    
    # 1. 检查目录和文件是否存在 (10分)
    if os.path.exists(deliverables_path) and os.path.isdir(deliverables_path):
        item_score = 10
        passed = True
        reason = "deliverables 目录已创建"
    else:
        item_score = 0
        passed = False
        reason = "未找到 deliverables 目录"
    score += item_score
    details.append({"item": "检查结果目录", "score": item_score, "max_score": 10, "passed": passed, "reason": reason})

    # 尝试寻找报告文件
    report_file = None
    if passed:
        files = os.listdir(deliverables_path)
        if files:
            report_file = os.path.join(deliverables_path, files[0]) # 假设第一个文件即报告

    if not report_file:
        details.append({"item": "数据内容检查", "score": 0, "max_score": 70, "passed": False, "reason": "未找到报告文件，无法验证数据"})
        score += 0
    else:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 2. 验证总人数 (20分)
        if str(EXPECTED_PEOPLE) in content:
            item_score = 20
            passed = True
            reason = f"报告正确识别了 {EXPECTED_PEOPLE} 位普通用餐者"
        else:
            item_score = 0
            passed = False
            reason = "报告未正确统计用餐人数 (期望值 32)"
        score += item_score
        details.append({"item": "用餐人数统计", "score": item_score, "max_score": 20, "passed": passed, "reason": reason})

        # 3. 验证采购计算准确性 (50分 - 每个食材12.5分)
        purchase_items = [
            ("Tortillas", 70),
            ("Chicken", 11.5),
            ("Cheese", 100),
            ("Sauce", 5)
        ]
        p_score = 0
        p_reasons = []
        for name, val in purchase_items:
            # 兼容整数和浮点数表示
            if str(val) in content or f"{val:.1f}" in content:
                p_score += 12.5
                p_reasons.append(f"{name} OK")
            else:
                p_reasons.append(f"{name} 错误")
        
        score += int(p_score)
        details.append({
            "item": "采购清单准确性", 
            "score": int(p_score), 
            "max_score": 50, 
            "passed": p_score == 50, 
            "reason": "; ".join(p_reasons)
        })

        # 4. LLM 验证报告格式与语气 (20分)
        # 必须包含正式报告的结构，且包含所有关键部分
        prompt = "Does this file provide a formal report including: 1. Total count of eaters, 2. Scaled ingredients, and 3. Shopping list (what to buy)? Is the tone professional but helpful?"
        if llm_judge_content(prompt, content):
            item_score = 20
            passed = True
            reason = "报告格式完整且语气符合要求"
        else:
            item_score = 0
            passed = False
            reason = "报告格式缺失关键模块或语气不专业"
        score += item_score
        details.append({"item": "报告质量评价(LLM)", "score": item_score, "max_score": 20, "passed": passed, "reason": reason})

    # 最终输出
    results = {
        "total_score": min(score, 100),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
