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

def extract_prices_and_total(json_data):
    items = []
    total = None
    
    if isinstance(json_data, dict):
        for k, v in json_data.items():
            if isinstance(v, list):
                items = v
            elif isinstance(v, (int, float)):
                total = float(v)
            elif isinstance(v, str):
                try:
                    total = float(v.replace('$', '').replace(',', ''))
                except ValueError:
                    pass
    elif isinstance(json_data, list):
        items = json_data
    
    # Extract prices from items
    prices = []
    for item in items:
        if isinstance(item, dict):
            for k, v in item.items():
                if isinstance(v, (int, float)):
                    prices.append(float(v))
                elif isinstance(v, str) and '$' in v:
                    try:
                        prices.append(float(v.replace('$', '').replace(',', '').strip()))
                    except ValueError:
                        pass
    
    # If total wasn't found as a top-level key, try to find an item representing the total
    if total is None:
        for item in items:
            if isinstance(item, dict):
                for k, v in item.items():
                    if 'total' in k.lower() and isinstance(v, (int, float)):
                        total = float(v)
                        
    return prices, total

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    summary_dir = os.path.join(workspace, "summary")
    json_path = os.path.join(summary_dir, "clothing_expenses.json")
    
    score_details = []
    total_score = 0
    
    # 1. Check directory existence
    if os.path.isdir(summary_dir):
        score_details.append({"item": "检查 summary 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "summary 目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 summary 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "summary 目录不存在"})
        
    # 2. Check JSON file existence and schema
    json_data = None
    if os.path.isfile(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_content = f.read()
                json_data = json.loads(json_content)
            score_details.append({"item": "检查 clothing_expenses.json 是否存在且为合法 JSON", "score": 15, "max_score": 15, "passed": True, "reason": "JSON 文件存在且格式合法"})
            total_score += 15
        except json.JSONDecodeError:
            score_details.append({"item": "检查 clothing_expenses.json 是否存在且为合法 JSON", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 文件存在但无法解析"})
    else:
        score_details.append({"item": "检查 clothing_expenses.json 是否存在且为合法 JSON", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 文件不存在"})
        
    if json_data is not None:
        prices, total = extract_prices_and_total(json_data)
        
        # 3. Exactly 4 items
        if len(prices) >= 4:
            score_details.append({"item": "提取商品数量", "score": 25, "max_score": 25, "passed": True, "reason": f"成功提取到至少4个价格记录 (发现 {len(prices)} 个)"})
            total_score += 25
        else:
            score_details.append({"item": "提取商品数量", "score": 0, "max_score": 25, "passed": False, "reason": f"未能找到4个独立的衣服价格记录 (仅发现 {len(prices)} 个)"})
            
        # 4. Total Calculation Validation
        if total is not None:
            # We check if the sum of items (or max possible sum combinations) matches total
            calculated_sum = sum(prices)
            # Sometimes 'total' is included in 'prices' list if schema is flat
            if abs(calculated_sum - total) < 0.01 or (prices and abs(sum(prices) - total * 2) < 0.01):
                score_details.append({"item": "核对总金额数学计算", "score": 25, "max_score": 25, "passed": True, "reason": "记录的总价与单项价格之和数学计算一致"})
                total_score += 25
            else:
                score_details.append({"item": "核对总金额数学计算", "score": 0, "max_score": 25, "passed": False, "reason": f"数学计算不匹配 (单项和:{calculated_sum}, 宣称总计:{total})"})
        else:
            score_details.append({"item": "核对总金额数学计算", "score": 0, "max_score": 25, "passed": False, "reason": "未能在 JSON 中明确提取到总金额字段"})
            
        # 5. LLM Semantic Check
        prompt = "Does this JSON correctly contain the decoded real names of vintage clothes, with absolutely NO raw catalog codes (like HVC-1950-CC), and completely excludes irrelevant items like 'groceries' or 'fishing gear'?"
        passed_llm = llm_judge_content(prompt, json.dumps(json_data))
        if passed_llm:
            score_details.append({"item": "利用大模型检查内容过滤和商品名解码", "score": 25, "max_score": 25, "passed": True, "reason": "大模型判定商品名已正确解码，且成功过滤无关支出"})
            total_score += 25
        else:
            score_details.append({"item": "利用大模型检查内容过滤和商品名解码", "score": 0, "max_score": 25, "passed": False, "reason": "大模型判定包含未解码的 HVC 代码或混入了无关支出(如钓鱼、杂货)"})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
