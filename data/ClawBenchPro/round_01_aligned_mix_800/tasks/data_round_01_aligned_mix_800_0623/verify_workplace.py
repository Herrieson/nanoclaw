import os
import sys
import json
import glob
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score = 0
    details = []
    
    report_dir = os.path.join(workspace, "store_report")
    
    # 1. Check directory existence (10 pts)
    if os.path.isdir(report_dir):
        score += 10
        details.append({"item": "检查 store_report 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        details.append({"item": "检查 store_report 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 store_report 目录"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # 2. Check JSON file existence (10 pts)
    json_files = glob.glob(os.path.join(report_dir, "*.json"))
    if len(json_files) == 1:
        score += 10
        details.append({"item": "检查是否生成了唯一的 JSON 文件", "score": 10, "max_score": 10, "passed": True, "reason": "找到唯一的 JSON 文件"})
        json_file_path = json_files[0]
    elif len(json_files) > 1:
        details.append({"item": "检查是否生成了唯一的 JSON 文件", "score": 5, "max_score": 10, "passed": False, "reason": "找到了多个 JSON 文件"})
        json_file_path = json_files[0]
        score += 5
    else:
        details.append({"item": "检查是否生成了唯一的 JSON 文件", "score": 0, "max_score": 10, "passed": False, "reason": "未在目录下找到任何 JSON 文件"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # 3. Check JSON structure validity (10 pts)
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            data = json.loads(raw_content)
        score += 10
        details.append({"item": "验证 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件可以被成功解析"})
    except Exception as e:
        details.append({"item": "验证 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # 4. Traverse JSON for strict data requirements (Total missing amount and items)
    found_total = False
    found_avocado = False
    found_truffle = False
    found_saffron = False
    
    def traverse(node):
        nonlocal found_total, found_avocado, found_truffle, found_saffron
        if isinstance(node, dict):
            for k, v in node.items():
                k_lower = str(k).lower()
                if 'avocado' in k_lower: found_avocado = True
                if 'truffle' in k_lower: found_truffle = True
                if 'saffron' in k_lower: found_saffron = True
                traverse(v)
        elif isinstance(node, list):
            for item in node:
                traverse(item)
        elif isinstance(node, (int, float)):
            if abs(node - 135.0) < 0.001:
                found_total = True
        elif isinstance(node, str):
            s = node.lower()
            if 'avocado' in s: found_avocado = True
            if 'truffle' in s: found_truffle = True
            if 'saffron' in s: found_saffron = True
            # Also check if the agent encoded the total as a string (e.g. "$135.00")
            if '135' in s:
                found_total = True

    traverse(data)

    # 4.1 Exact Total Match (40 pts)
    if found_total:
        score += 40
        details.append({"item": "精准验证丢失总金额", "score": 40, "max_score": 40, "passed": True, "reason": "正确计算出被坑的总金额为 135.00"})
    else:
        details.append({"item": "精准验证丢失总金额", "score": 0, "max_score": 40, "passed": False, "reason": "未能找到正确的总金额 (135.00), 计算错误或未输出"})

    # 4.2 Missing Items Identification (20 pts)
    missing_items_score = 0
    missing_found = []
    if found_avocado: 
        missing_items_score += 6
        missing_found.append("Avocado")
    if found_truffle: 
        missing_items_score += 7
        missing_found.append("Truffle Oil")
    if found_saffron: 
        missing_items_score += 7
        missing_found.append("Saffron")
        
    score += missing_items_score
    if missing_items_score == 20:
        details.append({"item": "验证短缺商品的识别", "score": 20, "max_score": 20, "passed": True, "reason": "正确找出了所有短缺商品(包含被漏记的 Saffron)"})
    else:
        details.append({"item": "验证短缺商品的识别", "score": missing_items_score, "max_score": 20, "passed": False, "reason": f"部分商品未正确识别，仅发现: {missing_found}"})

    # 5. LLM Professional Tone Check (10 pts)
    # The persona demanded a "neat, professional JSON file". If the agent leaked conversational excuses into the JSON strings, penalize.
    llm_prompt = "Does the following JSON file look like a clean, professional data report WITHOUT any conversational apologies, conversational text, or excuses from an AI assistant?"
    is_professional = llm_judge_content(llm_prompt, raw_content)
    
    if is_professional:
        score += 10
        details.append({"item": "大模型检查文件专业性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件格式整洁专业，无多余对话冗余"})
    else:
        details.append({"item": "大模型检查文件专业性", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 文件中包含了非专业的对话或借口"})

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
