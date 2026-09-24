import os
import sys
import json
import httpx
from openai import OpenAI

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
    """
    使用大模型验证非结构化自然语言文本，仅返回 True 或 False。
    """
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = os.path.join(workspace, "workplace_score.json")
    
    score = 0
    details = []
    
    # 1. 结构验证：检查报告输出目录
    plan_dir = os.path.join(workspace, "finished_plan")
    if os.path.isdir(plan_dir):
        score += 15
        details.append({"item": "检查 finished_plan 目录是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "目录 finished_plan 存在"})
    else:
        details.append({"item": "检查 finished_plan 目录是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "目录 finished_plan 不存在"})
        with open(score_file, "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 2. 结构验证：检查是否生成了报告文件
    try:
        files = os.listdir(plan_dir)
        report_files = [f for f in files if os.path.isfile(os.path.join(plan_dir, f))]
    except Exception as e:
        report_files = []
        
    if len(report_files) > 0:
        score += 15
        details.append({"item": "检查报告文件是否成功创建", "score": 15, "max_score": 15, "passed": True, "reason": f"成功找到报告文件: {report_files[0]}"})
    else:
        details.append({"item": "检查报告文件是否成功创建", "score": 0, "max_score": 15, "passed": False, "reason": "finished_plan 目录下未找到任何文件"})
        with open(score_file, "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 聚合读取报告文件的全部内容（Agent 可能将其命名为 report.txt, report.md 等）
    content = ""
    for f in report_files:
        try:
            with open(os.path.join(plan_dir, f), "r", encoding="utf-8") as file:
                content += file.read() + "\n"
        except:
            pass

    if not content.strip():
        details.append({"item": "检查报告内容是否为空", "score": 0, "max_score": 70, "passed": False, "reason": "报告文件内容为空"})
        with open(score_file, "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 3. 语义验证：是否正确剔除免费及废料物品，且精准锁定消费物品
    prompt_items = (
        "Does this report explicitly or implicitly list the items that were ACTUALLY PAID FOR "
        "(steering wheel, bolts and washers, steel axle, rubber wheels) AND strictly ignore "
        "or zero-out the free/scrap items (heavy duty glue, thick plastic sheets, brake cable, headlights, molded plastic seat)? "
        "Reply 'YES' only if it successfully separates the paid items from the free items."
    )
    if llm_judge_content(prompt_items, content):
        score += 30
        details.append({"item": "数据清洗能力与业务逻辑判断", "score": 30, "max_score": 30, "passed": True, "reason": "LLM 判定报告正确剔除了免费及工厂废料物品"})
    else:
        details.append({"item": "数据清洗能力与业务逻辑判断", "score": 0, "max_score": 30, "passed": False, "reason": "LLM 判定未能正确区分或遗漏了付费物品，业务逻辑错误"})

    # 4. 语义验证：总额计算准确性
    # 期望值 = 35.50 + 4.20 + 45.00 + 20.00 = 104.70
    prompt_total = (
        "Does this report explicitly state that the total cost is exactly $104.70 (or 104.7)? "
        "Look closely at the numbers in the text. Reply 'YES' only if this exact number is given as the final cost."
    )
    if llm_judge_content(prompt_total, content):
        score += 25
        details.append({"item": "验证总花销计算准确度", "score": 25, "max_score": 25, "passed": True, "reason": "LLM 判定报告中的总消费金额 (104.70) 计算精确无误"})
    else:
        details.append({"item": "验证总花销计算准确度", "score": 0, "max_score": 25, "passed": False, "reason": "LLM 判定报告中给出的总计金额错误或未找到数字 104.70"})

    # 5. 语义验证：预算结论提取
    prompt_budget = (
        "Does this report explicitly state whether the project is under the $200 budget? "
        "Reply 'YES' only if it clearly concludes that the spending is below the 200 budget limit."
    )
    if llm_judge_content(prompt_budget, content):
        score += 15
        details.append({"item": "预算执行情况汇报", "score": 15, "max_score": 15, "passed": True, "reason": "LLM 判定报告给出了明确的符合预算结论"})
    else:
        details.append({"item": "预算执行情况汇报", "score": 0, "max_score": 15, "passed": False, "reason": "LLM 判定未对是否满足 200 美元预算给出有效结论"})

    with open(score_file, "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
