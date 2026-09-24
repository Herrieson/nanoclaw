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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "garden_deliverables")
    
    score_details = []
    total_score = 0
    
    # 1. Check if directory exists
    dir_exists = os.path.isdir(deliverables_dir)
    if dir_exists:
        score_details.append({"item": "检查目标目录(garden_deliverables)是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标目录(garden_deliverables)是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录未创建"})
    
    # Read files in the directory
    all_text = ""
    file_found = False
    if dir_exists:
        for filename in os.listdir(deliverables_dir):
            file_path = os.path.join(deliverables_dir, filename)
            if os.path.isfile(file_path):
                file_found = True
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        all_text += f.read() + "\n"
                except Exception:
                    pass

    # 2. Check if file is generated
    if file_found:
        score_details.append({"item": "检查目标目录内是否有报告文件", "score": 10, "max_score": 10, "passed": True, "reason": "报告文件存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标目录内是否有报告文件", "score": 0, "max_score": 10, "passed": False, "reason": "无任何文件"})
        
    text_lower = all_text.lower()
    
    # 3. Check for valid names inclusion (Alice, Charlie, Eve, Grace)
    valid_names = ["alice", "charlie", "eve", "grace"]
    if file_found:
        missing_valid = [n.capitalize() for n in valid_names if n not in text_lower]
        if not missing_valid:
            score_details.append({"item": "检查报告中是否包含了所有批准名单中的参与者", "score": 20, "max_score": 20, "passed": True, "reason": "所有有效的参与者名字均出现"})
            total_score += 20
        else:
            score_details.append({"item": "检查报告中是否包含了所有批准名单中的参与者", "score": 0, "max_score": 20, "passed": False, "reason": f"遗漏了有效参与者: {', '.join(missing_valid)}"})
    else:
        score_details.append({"item": "检查报告中是否包含了所有批准名单中的参与者", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在，无法检查"})

    # 4. Check for strict exclusion of invalid names (Bob, David, Frank)
    invalid_names = ["bob", "david", "frank"]
    if file_found:
        included_invalid = [n.capitalize() for n in invalid_names if n in text_lower]
        if not included_invalid:
            score_details.append({"item": "检查报告是否严格剔除了请求入侵物种的参与者", "score": 20, "max_score": 20, "passed": True, "reason": "无入侵物种请求者出现"})
            total_score += 20
        else:
            score_details.append({"item": "检查报告是否严格剔除了请求入侵物种的参与者", "score": 0, "max_score": 20, "passed": False, "reason": f"错误地包含了无效参与者: {', '.join(included_invalid)}"})
    else:
        score_details.append({"item": "检查报告是否严格剔除了请求入侵物种的参与者", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在，无法检查"})

    # 5. Check for correct total valid hours calculation (14)
    if file_found:
        if re.search(r'\b14\b', all_text):
            score_details.append({"item": "检查报告中是否计算并包含了正确的总志愿小时数 (14)", "score": 20, "max_score": 20, "passed": True, "reason": "发现了正确的总时长数字"})
            total_score += 20
        else:
            score_details.append({"item": "检查报告中是否计算并包含了正确的总志愿小时数 (14)", "score": 0, "max_score": 20, "passed": False, "reason": "未找到正确的总小时数值14"})
    else:
        score_details.append({"item": "检查报告中是否计算并包含了正确的总志愿小时数 (14)", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在，无法检查"})

    # 6. LLM semantic check for "neatness" and format
    if file_found and len(all_text.strip()) > 0:
        llm_prompt = "Does the provided file content look like a neat, clear summary report for a community garden volunteer day, explicitly listing approved volunteers and their total pledged hours without random leftover raw code?"
        is_neat = llm_judge_content(llm_prompt, all_text[:2000]) # truncated to avoid token limit
        if is_neat:
            score_details.append({"item": "利用大模型检查报告语义与格式是否整洁规范", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定报告格式整洁规范"})
            total_score += 20
        else:
            score_details.append({"item": "利用大模型检查报告语义与格式是否整洁规范", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定报告格式不够整洁或语义不清"})
    else:
        score_details.append({"item": "利用大模型检查报告语义与格式是否整洁规范", "score": 0, "max_score": 20, "passed": False, "reason": "无有效文本，无法判定"})

    # Output JSON
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
