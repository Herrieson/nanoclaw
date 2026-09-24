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

def find_unapproved_in_json(data):
    target_set = {"Frank Castle", "Grace Lee", "Henry Todd"}
    if isinstance(data, dict):
        for v in data.values():
            if find_unapproved_in_json(v):
                return True
    elif isinstance(data, list):
        str_items = set(str(x).strip() for x in data)
        if target_set.issubset(str_items):
            return True
        for item in data:
            if find_unapproved_in_json(item):
                return True
    elif isinstance(data, str):
        if all(t in data for t in target_set):
            return True
    return False

def find_total_hours(data):
    if isinstance(data, dict):
        for v in data.values():
            if find_total_hours(v):
                return True
    elif isinstance(data, list):
        for item in data:
            if find_total_hours(item):
                return True
    elif isinstance(data, (int, float)):
        if abs(float(data) - 12.0) < 1e-5:
            return True
    elif isinstance(data, str):
        try:
            if abs(float(data) - 12.0) < 1e-5:
                return True
        except ValueError:
            pass
    return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    reports_dir = os.path.join(workspace, "reports")
    
    score_details = []
    total_score = 0
    
    # 1. 检查目录和 JSON 文件存在 (20分)
    json_files = []
    if os.path.isdir(reports_dir):
        json_files = glob.glob(os.path.join(reports_dir, "*.json"))
        if json_files:
            score_details.append({"item": "检查 reports 目录及 JSON 报告是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "成功找到 JSON 文件"})
            total_score += 20
        else:
            score_details.append({"item": "检查 reports 目录及 JSON 报告是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "reports 目录存在但缺少 JSON 文件"})
    else:
        score_details.append({"item": "检查 reports 目录及 JSON 报告是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "reports 目录不存在"})

    # 2. 检查数据准确度 (80分)
    json_valid = False
    data = None
    if json_files:
        for file in json_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    json_valid = True
                    break
            except json.JSONDecodeError:
                continue

    if not json_valid:
        score_details.append({"item": "JSON 文件是否格式合法且成功解析", "score": 0, "max_score": 10, "passed": False, "reason": "未找到格式合法的 JSON 报告"})
        score_details.append({"item": "是否正确提取未授权的志愿者名单", "score": 0, "max_score": 35, "passed": False, "reason": "未能解析 JSON"})
        score_details.append({"item": "是否正确计算出有效的 Under 5 总时长", "score": 0, "max_score": 35, "passed": False, "reason": "未能解析 JSON"})
    else:
        score_details.append({"item": "JSON 文件是否格式合法且成功解析", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件解析成功"})
        total_score += 10
        
        has_unapproved = find_unapproved_in_json(data)
        if has_unapproved:
            score_details.append({"item": "是否正确提取未授权的志愿者名单", "score": 35, "max_score": 35, "passed": True, "reason": "精确找到所有未授权的志愿者（Frank Castle, Grace Lee, Henry Todd）"})
            total_score += 35
        else:
            score_details.append({"item": "是否正确提取未授权的志愿者名单", "score": 0, "max_score": 35, "passed": False, "reason": "缺失部分或全部未授权志愿者的名字"})
            
        has_total_hours = find_total_hours(data)
        if has_total_hours:
            score_details.append({"item": "是否正确计算出有效的 Under 5 总时长", "score": 35, "max_score": 35, "passed": True, "reason": "正确排除了异常数据和非白名单人员，得到正确的 12.0 小时"})
            total_score += 35
        else:
            score_details.append({"item": "是否正确计算出有效的 Under 5 总时长", "score": 0, "max_score": 35, "passed": False, "reason": "时长计算错误或未找到正确的值(期望 12.0)"})

    # Write score logic
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
