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

def get_all_numeric_values(d):
    vals = []
    if isinstance(d, dict):
        for v in d.values():
            vals.extend(get_all_numeric_values(v))
    elif isinstance(d, list):
        for v in d:
            vals.extend(get_all_numeric_values(v))
    else:
        try:
            if isinstance(d, str):
                d = d.replace('$', '').replace(',', '')
            vals.append(float(d))
        except (ValueError, TypeError):
            pass
    return vals

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    accountant_dir = os.path.join(workspace, "accountant_ready")
    target_file = os.path.join(accountant_dir, "tax_headache_summary.json")
    
    # 1. Directory Check
    if os.path.isdir(accountant_dir):
        score_details.append({"item": "检查目标目录是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录 accountant_ready 存在"})
        total_score += 5
    else:
        score_details.append({"item": "检查目标目录是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "目录 accountant_ready 不存在"})
        
    # 2. File Check
    file_exists = os.path.isfile(target_file)
    if file_exists:
        score_details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 tax_headache_summary.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 tax_headache_summary.json 不存在"})
    
    # 3. JSON Validity & Data Checks
    json_data = None
    if file_exists:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()
                json_data = json.loads(content)
            score_details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件解析成功"})
            total_score += 10
        except json.JSONDecodeError:
            score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 文件格式错误"})
            content = ""
    else:
        score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失，无法解析"})
        content = ""

    # 4. Exact Math Checks (Code-based)
    if json_data is not None:
        numeric_vals = get_all_numeric_values(json_data)
        
        # Revenue check: Expected 4500
        if 4500.0 in numeric_vals:
            score_details.append({"item": "检查总收入计算精确度", "score": 30, "max_score": 30, "passed": True, "reason": "精确提取到总收入数值 4500"})
            total_score += 30
        else:
            score_details.append({"item": "检查总收入计算精确度", "score": 0, "max_score": 30, "passed": False, "reason": f"未提取到正确的总收入(4500)，实际提取数字: {numeric_vals}"})
            
        # Expenses check: Expected 830.50
        # If they included the bandana ($15), it might be 845.50
        if 830.5 in numeric_vals:
            score_details.append({"item": "检查总支出计算精确度(剔除个人消费)", "score": 30, "max_score": 30, "passed": True, "reason": "精确提取到总支出数值 830.5，且成功剔除了个人头巾消费"})
            total_score += 30
        elif 845.5 in numeric_vals:
            score_details.append({"item": "检查总支出计算精确度(剔除个人消费)", "score": 0, "max_score": 30, "passed": False, "reason": "未剔除 15 美元的个人头巾消费，金额错误 (845.5)"})
        else:
            score_details.append({"item": "检查总支出计算精确度(剔除个人消费)", "score": 0, "max_score": 30, "passed": False, "reason": f"未提取到正确的总支出(830.5)，实际提取数字: {numeric_vals}"})
            
        # 5. LLM Semantic Check
        prompt = "Does this JSON contain clear keys representing 'total revenue' and 'total deductible expenses' WITHOUT containing irrelevant personal items (like bandanas), extra conversational text, or hallucinated fields?"
        is_professional = llm_judge_content(prompt, content)
        if is_professional:
            score_details.append({"item": "利用大模型检查 JSON 语义是否专业简洁", "score": 15, "max_score": 15, "passed": True, "reason": "大模型判定 JSON 结构清晰、未包含多余或虚假信息"})
            total_score += 15
        else:
            score_details.append({"item": "利用大模型检查 JSON 语义是否专业简洁", "score": 0, "max_score": 15, "passed": False, "reason": "大模型判定 JSON 含有废话、多余字段或结构不符合要求"})
            
    else:
        score_details.append({"item": "检查总收入计算精确度", "score": 0, "max_score": 30, "passed": False, "reason": "未找到合法 JSON"})
        score_details.append({"item": "检查总支出计算精确度(剔除个人消费)", "score": 0, "max_score": 30, "passed": False, "reason": "未找到合法 JSON"})
        score_details.append({"item": "利用大模型检查 JSON 语义是否专业简洁", "score": 0, "max_score": 15, "passed": False, "reason": "未找到合法 JSON"})

    # Output Score
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
