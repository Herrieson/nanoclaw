import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型进行非结构化语义及复杂条件的严格检测接口"""
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

def extract_all_numbers(data):
    """防御性编程：递归提取任意复杂度的 JSON 数据中的所有数字，防止 Agent 任意嵌套结构"""
    nums = []
    if isinstance(data, dict):
        for v in data.values():
            nums.extend(extract_all_numbers(v))
    elif isinstance(data, list):
        for v in data:
            nums.extend(extract_all_numbers(v))
    elif isinstance(data, (int, float)):
        nums.append(float(data))
    elif isinstance(data, str):
        # 尝试转换字符串数字，例如 "446.4"
        try:
            nums.append(float(data.replace('$', '').replace(',', '').strip()))
        except ValueError:
            pass
    return nums

def verify_workplace(workspace_dir):
    results = []
    total_score = 0
    target_file = os.path.join(workspace_dir, "financial_forecast", "dinner_budget.json")

    # 1. 验证报告目录与文件是否存在 (15分)
    file_exists = os.path.exists(target_file)
    if file_exists:
        results.append({"item": "检查目标文件是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "找到了 dinner_budget.json 文件。"})
        total_score += 15
    else:
        results.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "缺失 financial_forecast/dinner_budget.json 文件。"})
    
    # 后续验证依赖于文件存在
    if file_exists:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content_str = f.read()
                json_data = json.loads(content_str)
                
            results.append({"item": "验证 JSON 格式合法性", "score": 15, "max_score": 15, "passed": True, "reason": "成功解析 JSON 结构。"})
            total_score += 15
            
            # 2. 核心数值确定性验证：总成本 (40分)
            # 根据逻辑：
            # Lobster (Base=100, Cur=120, USD, flag *) -> 120 * 1.2 = 144
            # Oysters (Base=50, Cur=52, USD) -> 52
            # Chardonnay (Base=80, Cur=95, EUR, flag *) -> 95 * 1.10 = 104.5 -> 104.5 * 1.2 = 125.4
            # Pinot Noir (Base=120, Cur=125, USD) -> 125
            # Total = 144 + 52 + 125.4 + 125 = 446.4
            all_numbers = extract_all_numbers(json_data)
            cost_passed = any(abs(n - 446.4) < 0.05 for n in all_numbers)
            
            if cost_passed:
                results.append({"item": "验证最终预算总金额 (精确匹配计算逻辑)", "score": 40, "max_score": 40, "passed": True, "reason": "在 JSON 中准确找到了符合金融计算预期的总金额 446.4。"})
                total_score += 40
            else:
                results.append({"item": "验证最终预算总金额 (精确匹配计算逻辑)", "score": 0, "max_score": 40, "passed": False, "reason": f"未找到精确值 446.4。提取到的数字有: {all_numbers}"})
            
            # 3. 语义与业务规则判定：涨幅超过15%的商品及 JSON 清洁度 (30分)
            # Lobster涨幅: 20%; Chardonnay涨幅: 18.75%; Oysters: 4%; Pinot Noir: 4.16%
            # 应只有 Lobster 和 Chardonnay 被标记。
            prompt_text = (
                "You are auditing a strict JSON report regarding financial forecasting. "
                "Evaluate the following rules:\n"
                "1. Does the JSON explicitly identify ONLY 'Lobster' and 'Chardonnay' as the flagged items (or items with > 15% price spike)?\n"
                "2. It MUST NOT flag 'Oysters' or 'Pinot Noir' for spikes.\n"
                "3. The JSON must be clean and not contain conversational filler (like 'Here is your budget').\n"
                "Return YES if ALL conditions are met, otherwise NO."
            )
            llm_passed = llm_judge_content(prompt_text, content_str)
            if llm_passed:
                results.append({"item": "利用大模型检查通胀预警标记准确度及结构纯净度", "score": 30, "max_score": 30, "passed": True, "reason": "LLM 判定成功标记了 Lobster 和 Chardonnay，且无幻觉或冗余对话。"})
                total_score += 30
            else:
                results.append({"item": "利用大模型检查通胀预警标记准确度及结构纯净度", "score": 0, "max_score": 30, "passed": False, "reason": "LLM 判定标记项错误（包含多余/漏掉成分）或 JSON 存在冗余自然语言。"})
                
        except json.JSONDecodeError:
            results.append({"item": "验证 JSON 格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": "生成的文件非合法 JSON。"})
            results.append({"item": "验证最终预算总金额", "score": 0, "max_score": 40, "passed": False, "reason": "无法读取内容。"})
            results.append({"item": "利用大模型检查通胀预警标记准确度", "score": 0, "max_score": 30, "passed": False, "reason": "无法读取内容。"})
    else:
        # 文件不存在时补充占位
        results.append({"item": "验证 JSON 格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": "文件不存在。"})
        results.append({"item": "验证最终预算总金额", "score": 0, "max_score": 40, "passed": False, "reason": "文件不存在。"})
        results.append({"item": "利用大模型检查通胀预警标记准确度", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在。"})

    # 输出结果
    output_data = {
        "total_score": total_score,
        "details": results
    }
    
    with open(os.path.join(workspace_dir, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
        
    print(f"Workplace Verification Completed. Total Score: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
