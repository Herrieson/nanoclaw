import os
import sys
import json
import httpx
from openai import OpenAI

# 强制要求的大模型配置
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
    report_path = os.path.join(workspace, "reports", "manager_report.json")
    
    score_details = []
    total_score = 0
    
    # 1. Check directory and file existence & schema (20 points)
    file_exists = os.path.exists(report_path)
    report_data = None
    if file_exists:
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
                report_data = json.loads(content)
            score_details.append({"item": "报告文件及格式检查", "score": 20, "max_score": 20, "passed": True, "reason": "manager_report.json 存在且为合法 JSON"})
            total_score += 20
        except json.JSONDecodeError:
            score_details.append({"item": "报告文件及格式检查", "score": 0, "max_score": 20, "passed": False, "reason": "manager_report.json 不是合法的 JSON 文件"})
    else:
        score_details.append({"item": "报告文件及格式检查", "score": 0, "max_score": 20, "passed": False, "reason": "找不到 reports/manager_report.json"})

    if report_data:
        # 2. Check total_revenue (25 points)
        # Expected: 15+8+10+15+15+8+6+15+15 = 107.0
        revenue = report_data.get("total_revenue")
        if revenue is not None and (isinstance(revenue, (int, float)) and abs(float(revenue) - 107.0) < 0.01):
            score_details.append({"item": "计算总收入 (total_revenue)", "score": 25, "max_score": 25, "passed": True, "reason": "成功算出准确的总收入 107.0"})
            total_score += 25
        else:
            score_details.append({"item": "计算总收入 (total_revenue)", "score": 0, "max_score": 25, "passed": False, "reason": f"total_revenue 计算错误，期望 107.0，实际 {revenue}"})

        # 3. Check chad_errors (25 points)
        # Expected: Chorizo (charged 10 instead of 12), Manchego Cheese (charged 15 instead of 20)
        errors = report_data.get("chad_errors")
        if isinstance(errors, list):
            normalized_errors = sorted([str(e).strip().lower() for e in errors])
            expected = ["chorizo", "manchego cheese"]
            if normalized_errors == expected:
                score_details.append({"item": "筛查 Chad 的错误 (chad_errors)", "score": 25, "max_score": 25, "passed": True, "reason": "精准找出了 Chad 标错价格的商品"})
                total_score += 25
            else:
                score_details.append({"item": "筛查 Chad 的错误 (chad_errors)", "score": 0, "max_score": 25, "passed": False, "reason": f"商品错误列表不符合预期，实际 {errors}"})
        else:
             score_details.append({"item": "筛查 Chad 的错误 (chad_errors)", "score": 0, "max_score": 25, "passed": False, "reason": "chad_errors 字段缺失或不是列表"})

        # 4. Check can_cook_tonight (20 points)
        # Expected: Saffron starts at 10, sold 4 (tx 1, 4, 8, 9), left 6. Recipe needs 7. So False.
        can_cook = report_data.get("can_cook_tonight")
        if can_cook is False or str(can_cook).strip().lower() == "false":
            score_details.append({"item": "校验今晚是否能做饭 (can_cook_tonight)", "score": 20, "max_score": 20, "passed": True, "reason": "库存扣减逻辑正确，得出了正确结论 False"})
            total_score += 20
        else:
             score_details.append({"item": "校验今晚是否能做饭 (can_cook_tonight)", "score": 0, "max_score": 20, "passed": False, "reason": f"库存推理错误，期望 False，实际 {can_cook}"})

        # 5. LLM Strict Check: No extra fluff (10 points)
        # User explicitly says "I don't have all day", so the JSON should be purely data.
        prompt = "Does this JSON string contain any extra conversational text, apologies, personal opinions, or keys other than 'total_revenue', 'chad_errors', and 'can_cook_tonight'? Answer YES if it contains extra conversational fluff/keys, NO if it is clean and strictly data."
        has_fluff = llm_judge_content(prompt, json.dumps(report_data))
        if not has_fluff:
            score_details.append({"item": "利用大模型检查废话与幻觉", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 非常干净，没有引入无用的字段或寒暄"})
            total_score += 10
        else:
            score_details.append({"item": "利用大模型检查废话与幻觉", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定报告中包含多余的字段或废话，违反了用户的急躁情绪要求"})
    else:
        # File doesn't exist or invalid JSON, skip detailed checks
        score_details.extend([
            {"item": "计算总收入 (total_revenue)", "score": 0, "max_score": 25, "passed": False, "reason": "文件缺失无法解析"},
            {"item": "筛查 Chad 的错误 (chad_errors)", "score": 0, "max_score": 25, "passed": False, "reason": "文件缺失无法解析"},
            {"item": "校验今晚是否能做饭 (can_cook_tonight)", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失无法解析"},
            {"item": "利用大模型检查废话与幻觉", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失无法解析"}
        ])

    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
