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

def extract_all_values(obj):
    """Recursively extract all values from a JSON-like object."""
    vals = []
    if isinstance(obj, dict):
        for v in obj.values():
            vals.extend(extract_all_values(v))
    elif isinstance(obj, list):
        for item in obj:
            vals.extend(extract_all_values(item))
    else:
        vals.append(obj)
    return vals

def is_close(a, b, tol=0.1):
    try:
        return abs(float(a) - float(b)) <= tol
    except (ValueError, TypeError):
        return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    dashboard_dir = os.path.join(workspace, "dashboard_api")
    
    # 1. Check Directory (10 pts)
    if os.path.isdir(dashboard_dir):
        total_score += 10
        score_details.append({"item": "检查目标目录 dashboard_api 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建了 dashboard_api 目录。"})
    else:
        score_details.append({"item": "检查目标目录 dashboard_api 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 dashboard_api 目录。"})
        # Write immediate failure if directory doesn't exist
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. Check JSON File Existence and Format (10 pts)
    json_files = glob.glob(os.path.join(dashboard_dir, "*.json"))
    if not json_files:
        score_details.append({"item": "检查是否生成了 JSON 文件", "score": 0, "max_score": 10, "passed": False, "reason": "dashboard_api 目录下没有找到任何 JSON 文件。"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return
        
    target_file = json_files[0]
    try:
        with open(target_file, "r") as f:
            raw_content = f.read()
            data = json.loads(raw_content)
        total_score += 10
        score_details.append({"item": "检查 JSON 文件格式", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件存在且能够成功反序列化。"})
    except json.JSONDecodeError:
        score_details.append({"item": "检查 JSON 文件格式", "score": 0, "max_score": 10, "passed": False, "reason": "生成的文件不是有效的 JSON 格式。"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. Code-based Data Extraction & Validation (60 pts total)
    # Get all leaf values from JSON
    all_values = extract_all_values(data)
    
    # 3.1 Check Total Miles: 1500.0 (20 pts)
    miles_found = any(is_close(v, 1500.0) for v in all_values)
    if miles_found:
        total_score += 20
        score_details.append({"item": "精确验证: 总里程计算", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取并计算出总里程 1500.0。"})
    else:
        score_details.append({"item": "精确验证: 总里程计算", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 的值中未能找到正确的总里程数 1500.0。"})

    # 3.2 Check Total Fuel Spend: 475.85 (20 pts)
    fuel_found = any(is_close(v, 475.85, tol=0.02) for v in all_values)
    if fuel_found:
        total_score += 20
        score_details.append({"item": "精确验证: 总燃油花费计算", "score": 20, "max_score": 20, "passed": True, "reason": "成功清洗 CSV 并计算出总燃油费 475.85。"})
    else:
        score_details.append({"item": "精确验证: 总燃油花费计算", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 的值中未能找到正确的总燃油费 475.85。"})

    # 3.3 Check Longest Idle City: Gary (20 pts)
    city_found = any(isinstance(v, str) and "gary" in v.lower() for v in all_values)
    if city_found:
        total_score += 20
        score_details.append({"item": "精确验证: 最长怠速城市分析", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析行车记录仪日志并找出最长停留城市 Gary。"})
    else:
        score_details.append({"item": "精确验证: 最长怠速城市分析", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 的值中未能找到城市 'Gary'。"})

    # 4. LLM Semantic & Hallucination Check (20 pts)
    prompt = (
        "Review the following JSON content. "
        "Does it clearly have keys/labels that represent 'total fuel spend', 'total miles driven', and 'longest idle city', "
        "AND does it NOT contain any extra hallucinated data (like driver name, random weather info, or verbose explanations)? "
        "Reply 'YES' if the keys are clear and concise and no extra garbage data exists, otherwise 'NO'."
    )
    is_semantic_clean = llm_judge_content(prompt, raw_content)
    if is_semantic_clean:
        total_score += 20
        score_details.append({"item": "LLM 语义验证: 键名清晰度与无幻觉检测", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定 JSON 键名表意清晰，且无多余捏造数据。"})
    else:
        score_details.append({"item": "LLM 语义验证: 键名清晰度与无幻觉检测", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定 JSON 的键名不清晰，或夹杂了无用的幻觉字段。"})

    # Output final score
    with open("workplace_score.json", "w") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
