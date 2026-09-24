import os
import sys
import json
import httpx
import glob
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

def extract_numbers(data):
    nums = []
    if isinstance(data, dict):
        for v in data.values():
            nums.extend(extract_numbers(v))
    elif isinstance(data, list):
        for item in data:
            nums.extend(extract_numbers(item))
    elif isinstance(data, (int, float)):
        nums.append(float(data))
    elif isinstance(data, str):
        try:
            nums.append(float(data))
        except ValueError:
            pass
    return nums

def extract_strings(data):
    strs = []
    if isinstance(data, dict):
        for v in data.values():
            strs.extend(extract_strings(v))
    elif isinstance(data, list):
        for item in data:
            strs.extend(extract_strings(item))
    elif isinstance(data, str):
        strs.append(data.strip().lower())
    return strs

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []

    deliverables_dir = os.path.join(workspace, "deliverables")
    
    # 1. Check if directory exists
    if os.path.isdir(deliverables_dir):
        total_score += 15
        details.append({"item": "检查 deliverables 目录是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "目录 deliverables 存在"})
    else:
        details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "目录 deliverables 不存在"})
        
    json_files = []
    if os.path.isdir(deliverables_dir):
        json_files = glob.glob(os.path.join(deliverables_dir, "*.json"))

    # 2. Check if a JSON file exists and is valid
    report_data = None
    report_content_str = ""
    if json_files:
        try:
            with open(json_files[0], "r", encoding="utf-8") as f:
                report_content_str = f.read()
                report_data = json.loads(report_content_str)
            total_score += 15
            details.append({"item": "检查是否生成了有效的 JSON 报告文件", "score": 15, "max_score": 15, "passed": True, "reason": f"成功解析 {os.path.basename(json_files[0])}"})
        except Exception as e:
            details.append({"item": "检查是否生成了有效的 JSON 报告文件", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON 解析失败: {e}"})
    else:
        details.append({"item": "检查是否生成了有效的 JSON 报告文件", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 JSON 报告文件"})

    # 3. Check for total valid hours (18.5)
    # 4. Check for unapproved volunteers
    if report_data is not None:
        numbers = extract_numbers(report_data)
        strings = extract_strings(report_data)
        
        # Valid hours check
        if 18.5 in numbers:
            total_score += 30
            details.append({"item": "精准验证有效志愿者总工时", "score": 30, "max_score": 30, "passed": True, "reason": "正确计算出有效总工时 18.5 小时"})
        else:
            details.append({"item": "精准验证有效志愿者总工时", "score": 0, "max_score": 30, "passed": False, "reason": f"未在报告中找到正确的总工时数值 18.5，提取到的数值为: {numbers}"})
            
        # Unapproved volunteers check
        gary_flagged = any("gary smith" in s for s in strings)
        melissa_flagged = any("melissa vance" in s for s in strings)
        if gary_flagged and melissa_flagged:
            total_score += 30
            details.append({"item": "精准验证未获批违规人员名单", "score": 30, "max_score": 30, "passed": True, "reason": "正确标记出了 Gary Smith 和 Melissa Vance"})
        elif gary_flagged or melissa_flagged:
            total_score += 15
            details.append({"item": "精准验证未获批违规人员名单", "score": 15, "max_score": 30, "passed": False, "reason": "仅标记出了部分违规人员"})
        else:
            details.append({"item": "精准验证未获批违规人员名单", "score": 0, "max_score": 30, "passed": False, "reason": "未能提取或标记出任何违规人员名字"})
            
        # 5. LLM Semantic Check on JSON format formality
        prompt = "Does the following JSON content look like a formal report for volunteer hours, clearly categorizing 'valid hours' and 'flagged unapproved individuals' without redundant or hallucinated keys?"
        is_formal = llm_judge_content(prompt, report_content_str)
        if is_formal:
            total_score += 10
            details.append({"item": "大模型检查 JSON 报告的格式严肃性与结构合理性", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定报告结构合理且正式"})
        else:
            details.append({"item": "大模型检查 JSON 报告的格式严肃性与结构合理性", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定报告结构混乱或包含幻觉字段"})
            
    else:
        details.append({"item": "精准验证有效志愿者总工时", "score": 0, "max_score": 30, "passed": False, "reason": "无可用 JSON 数据"})
        details.append({"item": "精准验证未获批违规人员名单", "score": 0, "max_score": 30, "passed": False, "reason": "无可用 JSON 数据"})
        details.append({"item": "大模型检查 JSON 报告的格式严肃性与结构合理性", "score": 0, "max_score": 10, "passed": False, "reason": "无可用 JSON 数据"})

    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
