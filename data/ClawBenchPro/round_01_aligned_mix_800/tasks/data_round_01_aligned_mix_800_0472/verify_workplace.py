import os
import sys
import json
import httpx
import re
from openai import OpenAI

# 配置常量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """检测非结构化文本的统一接口"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        res = response.choices[0].message.content.strip().lower()
        return "yes" in res
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "finished_plan/budget_report.txt")
    score_details = []
    total_score = 0

    # 1. 检查结果文件是否存在 (10分)
    if os.path.exists(report_path):
        score_details.append({"item": "Check report existence", "score": 10, "max_score": 10, "passed": True, "reason": "Report file exists."})
        total_score += 10
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        score_details.append({"item": "Check report existence", "score": 0, "max_score": 10, "passed": False, "reason": "budget_report.txt not found."})
        content = ""

    # 2. 检查关键结论：BUSTED IT 或 UNDER BUDGET (20分)
    # 根据 Idea 链路，正确总价应为 215.50，超过 200，应为 BUSTED IT
    if content:
        has_busted = "BUSTED IT" in content
        has_under = "UNDER BUDGET" in content
        
        if has_busted and not has_under:
            score_details.append({"item": "Budget status check (BUSTED IT)", "score": 20, "max_score": 20, "passed": True, "reason": "Correctly identified as BUSTED IT."})
            total_score += 20
        elif has_under:
            score_details.append({"item": "Budget status check (BUSTED IT)", "score": 0, "max_score": 20, "passed": False, "reason": "Incorrectly identified as UNDER BUDGET."})
        else:
            score_details.append({"item": "Budget status check (BUSTED IT)", "score": 0, "max_score": 20, "passed": False, "reason": "Missing required status phrase."})

    # 3. 检查数值准确性 (50分)
    # 正确数值：35.50 (T-K1) + 85.00 (T-K2) + 95.00 (T-K3) = 215.50
    if content:
        # 使用正则提取数值
        numbers = re.findall(r"215\.50|215\.5", content)
        if numbers:
            score_details.append({"item": "Calculated total accuracy", "score": 50, "max_score": 50, "passed": True, "reason": "Total cost correctly calculated as 215.50."})
            total_score += 50
        else:
            # 容错：如果是解析到了部分数值或由于浮点误差
            if "215" in content:
                score_details.append({"item": "Calculated total accuracy", "score": 20, "max_score": 50, "passed": False, "reason": "Close but inaccurate value found."})
                total_score += 20
            else:
                score_details.append({"item": "Calculated total accuracy", "score": 0, "max_score": 50, "passed": False, "reason": "Correct total 215.50 not found."})

    # 4. LLM 语义检查：检查语气和格式是否符合要求 (20分)
    if content:
        prompt = "Does this report clearly state the final total cost and use a helpful tone to address the user's situation with his wife?"
        if llm_judge_content(prompt, content):
            score_details.append({"item": "Report quality and clarity", "score": 20, "max_score": 20, "passed": True, "reason": "LLM verified report clarity and tone."})
            total_score += 20
        else:
            score_details.append({"item": "Report quality and clarity", "score": 0, "max_score": 20, "passed": False, "reason": "LLM found report quality insufficient."})

    # 输出结果
    result = {
        "total_score": int(total_score),
        "details": score_details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
