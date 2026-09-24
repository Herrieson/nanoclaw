import os
import sys
import json
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

def extract_ids(data, ids_set):
    if isinstance(data, dict):
        if "id" in data and isinstance(data["id"], str):
            ids_set.add(data["id"])
        for v in data.values():
            extract_ids(v, ids_set)
    elif isinstance(data, list):
        for item in data:
            extract_ids(item, ids_set)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_dir = os.path.join(workspace, "policy_sorting")
    
    details = []
    total_score = 0
    
    # 1. Check Directory
    dir_exists = os.path.isdir(target_dir)
    if dir_exists:
        details.append({"item": "检查 policy_sorting 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已创建"})
        total_score += 10
    else:
        details.append({"item": "检查 policy_sorting 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 policy_sorting 目录"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=4)
        return

    # 2. Check JSON Files count and types
    files_in_dir = os.listdir(target_dir)
    json_files = [f for f in files_in_dir if f.lower().endswith(".json")]
    text_files = [f for f in files_in_dir if not f.lower().endswith(".json")]
    
    if len(json_files) == 2:
        details.append({"item": "检查是否刚好存在两个 JSON 文件分类", "score": 10, "max_score": 10, "passed": True, "reason": "找到了 2 个 JSON 文件"})
        total_score += 10
    else:
        details.append({"item": "检查是否刚好存在两个 JSON 文件分类", "score": 0, "max_score": 10, "passed": False, "reason": f"找到了 {len(json_files)} 个 JSON 文件，应为 2 个"})

    # 3. Validate JSON contents (High Risk and Standard)
    expected_high_risk = {"A102", "A103", "A104"}
    expected_standard = {"A101", "A105", "A106"}
    
    high_risk_score = 0
    standard_score = 0
    high_risk_found = False
    standard_found = False
    
    for jf in json_files:
        try:
            with open(os.path.join(target_dir, jf), 'r') as f:
                data = json.load(f)
            
            ids = set()
            extract_ids(data, ids)
            
            # Determine which bucket this is based on its contents
            if ids & expected_high_risk:
                # It's meant to be the high risk bucket
                high_risk_found = True
                if ids == expected_high_risk:
                    high_risk_score = 30
                    details.append({"item": "验证高风险客户名单完整且准确", "score": 30, "max_score": 30, "passed": True, "reason": f"高风险客户提取准确: {ids}"})
                else:
                    details.append({"item": "验证高风险客户名单完整且准确", "score": 0, "max_score": 30, "passed": False, "reason": f"高风险客户不匹配，提取出: {ids}"})
            elif ids & expected_standard:
                # It's meant to be the standard bucket
                standard_found = True
                if ids == expected_standard:
                    standard_score = 30
                    details.append({"item": "验证标准客户名单完整且准确", "score": 30, "max_score": 30, "passed": True, "reason": f"标准客户提取准确: {ids}"})
                else:
                    details.append({"item": "验证标准客户名单完整且准确", "score": 0, "max_score": 30, "passed": False, "reason": f"标准客户不匹配，提取出: {ids}"})
        except Exception as e:
            details.append({"item": f"解析 {jf} 时出现异常", "score": 0, "max_score": 0, "passed": False, "reason": str(e)})

    if not high_risk_found:
        details.append({"item": "验证高风险客户名单完整且准确", "score": 0, "max_score": 30, "passed": False, "reason": "未找到包含任何高风险客户数据的 JSON 文件"})
    if not standard_found:
        details.append({"item": "验证标准客户名单完整且准确", "score": 0, "max_score": 30, "passed": False, "reason": "未找到包含任何标准客户数据的 JSON 文件"})
        
    total_score += (high_risk_score + standard_score)

    # 4. Validate Total Dependents (10)
    children_score = 0
    children_passed = False
    
    if len(text_files) > 0:
        for tf in text_files:
            file_path = os.path.join(target_dir, tf)
            if not os.path.isfile(file_path):
                continue
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Code-based strict check
            if re.search(r'\b10\b', content):
                children_passed = True
                break
            
            # LLM semantic check in case it's written as "ten"
            if llm_judge_content("Does the text state that the total number of children/dependents is 10 (or 'ten')?", content):
                children_passed = True
                break
                
        if children_passed:
            children_score = 20
            details.append({"item": "检查是否正确计算了所有客户的子女总数", "score": 20, "max_score": 20, "passed": True, "reason": "成功在文本记录中找到正确的总数 10"})
        else:
            details.append({"item": "检查是否正确计算了所有客户的子女总数", "score": 0, "max_score": 20, "passed": False, "reason": "文本文件中未记录正确的总数 10"})
    else:
        details.append({"item": "检查是否正确计算了所有客户的子女总数", "score": 0, "max_score": 20, "passed": False, "reason": "未找到记录总数额的额外文本文件"})

    total_score += children_score

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=4)

if __name__ == "__main__":
    main()
