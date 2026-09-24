import os
import sys
import json
import glob
import re
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

def extract_strings(data):
    if isinstance(data, dict):
        res = []
        for k, v in data.items():
            res.append(str(k))
            res.extend(extract_strings(v))
        return res
    elif isinstance(data, list):
        res = []
        for item in data:
            res.extend(extract_strings(item))
        return res
    elif isinstance(data, str):
        return [data]
    else:
        return []

def extract_numbers(data):
    if isinstance(data, dict):
        res = []
        for v in data.values():
            res.extend(extract_numbers(v))
        return res
    elif isinstance(data, list):
        res = []
        for item in data:
            res.extend(extract_numbers(item))
        return res
    elif isinstance(data, (int, float)) and not isinstance(data, bool):
        return [data]
    elif isinstance(data, str):
        found = re.findall(r'\b\d+\b', data)
        return [int(x) for x in found]
    else:
        return []

def write_score(total_score, details, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []
    
    event_prep_dir = os.path.join(workspace, "event_prep")
    
    # 1. 检查结果目录是否存在 (10分)
    if os.path.isdir(event_prep_dir):
        total_score += 10
        details.append({"item": "检查目标目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "event_prep 目录已成功创建"})
    else:
        details.append({"item": "检查目标目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 event_prep 目录"})
        write_score(total_score, details, workspace)
        return
        
    # 2. 检查 JSON 文件是否存在 (10分)
    json_files = glob.glob(os.path.join(event_prep_dir, "*.json"))
    if not json_files:
        details.append({"item": "检查是否存在 JSON 文件", "score": 0, "max_score": 10, "passed": False, "reason": "event_prep 目录下没有找到任何 .json 文件"})
        write_score(total_score, details, workspace)
        return
        
    valid_json_data = None
    json_file_path = None
    raw_content = ""
    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                raw_content = f.read()
                valid_json_data = json.loads(raw_content)
                json_file_path = jf
                break
        except Exception:
            continue
            
    if valid_json_data is not None:
        total_score += 10
        details.append({"item": "检查是否存在格式合法的 JSON 文件", "score": 10, "max_score": 10, "passed": True, "reason": f"成功解析文件 {os.path.basename(json_file_path)}"})
    else:
        details.append({"item": "检查是否存在格式合法的 JSON 文件", "score": 0, "max_score": 10, "passed": False, "reason": "存在 .json 文件但格式不合法，无法被原生 JSON 库解析"})
        write_score(total_score, details, workspace)
        return
        
    # 解析出所有的字符串和数字
    strings = extract_strings(valid_json_data)
    numbers = extract_numbers(valid_json_data)
    
    has_alice = any("Alice M" in s for s in strings)
    has_david = any("David K" in s for s in strings)
    has_others = any(bad in s for s in strings for bad in ["Bob", "Charlie", "Eve", "Frank"])
    
    # 3. 检查受邀者命中情况 (共 35 分)
    if has_alice:
        total_score += 10
        details.append({"item": "检查是否包含有效受邀者 Alice M.", "score": 10, "max_score": 10, "passed": True, "reason": "数据中正确包含了 Alice M."})
    else:
        details.append({"item": "检查是否包含有效受邀者 Alice M.", "score": 0, "max_score": 10, "passed": False, "reason": "数据中未包含应出席的 Alice M."})
        
    if has_david:
        total_score += 10
        details.append({"item": "检查是否包含有效受邀者 David K.", "score": 10, "max_score": 10, "passed": True, "reason": "数据中正确包含了 David K."})
    else:
        details.append({"item": "检查是否包含有效受邀者 David K.", "score": 0, "max_score": 10, "passed": False, "reason": "数据中未包含应出席的 David K."})
        
    if not has_others:
        total_score += 15
        details.append({"item": "检查是否严格剔除了未达标的受邀者", "score": 15, "max_score": 15, "passed": True, "reason": "完美剔除了未确认或未携带艺术品的受邀者(Bob/Charlie/Eve/Frank)"})
    else:
        details.append({"item": "检查是否严格剔除了未达标的受邀者", "score": 0, "max_score": 15, "passed": False, "reason": "数据中错误地包含了未确认或未携带艺术品的受邀者，存在交叉验证失败"})
        
    # 4. 检查计算的精确总人数 (25分)
    # 计算逻辑: Alice (1+1) + David (1+0) = 3 
    if 3 in numbers:
        total_score += 25
        details.append({"item": "检查最终提取的参与总人数(包含家属)", "score": 25, "max_score": 25, "passed": True, "reason": "完美计算出精确人数 3"})
    else:
        details.append({"item": "检查最终提取的参与总人数(包含家属)", "score": 0, "max_score": 25, "passed": False, "reason": f"总人数计算错误，期望包含数字 3，实际解析出的数字有: {numbers}"})
        
    # 5. LLM 检测 JSON 结构的纯粹性，防止幻觉作弊 (20分)
    prompt = "The provided text is a JSON file generated by an AI assistant. The user strictly requested a clean JSON file for a ticketing app, containing ONLY final guest names and final headcount numbers. Check if the JSON is strictly structured data WITHOUT any conversational fluff, generated greetings, or meta-comments (like 'message': 'Here is your data'). Does it look like a pure, production-ready data JSON? Answer YES or NO."
    
    is_clean = llm_judge_content(prompt, raw_content)
    if is_clean:
        total_score += 20
        details.append({"item": "大模型检查 JSON 数据结构的纯粹性", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定 JSON 数据非常干净，无冗余对话及捏造的聊天节点"})
    else:
        details.append({"item": "大模型检查 JSON 数据结构的纯粹性", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定 JSON 包含非结构化聊天内容或冗余说明(幻觉)"})
        
    write_score(total_score, details, workspace)

if __name__ == "__main__":
    main()
