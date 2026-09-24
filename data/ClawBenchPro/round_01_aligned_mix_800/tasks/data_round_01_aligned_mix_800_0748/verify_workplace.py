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

def find_value_in_json(json_obj, target_value, is_list=False):
    """Recursively search for a specific value in a parsed JSON object."""
    if isinstance(json_obj, dict):
        for v in json_obj.values():
            if find_value_in_json(v, target_value, is_list):
                return True
    elif isinstance(json_obj, list):
        if is_list:
            # Check if the list contains exactly the same elements (order agnostic)
            if len(json_obj) == len(target_value) and set(json_obj) == set(target_value):
                return True
        for item in json_obj:
            if find_value_in_json(item, target_value, is_list):
                return True
    else:
        if not is_list:
            try:
                # Handle float comparisons
                if isinstance(target_value, float) and isinstance(json_obj, (int, float)):
                    if abs(float(json_obj) - target_value) < 0.01:
                        return True
            except (ValueError, TypeError):
                pass
    return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    deliverables_dir = os.path.join(workspace, "deliverables")
    report_file = os.path.join(deliverables_dir, "board_report.json")
    
    # 1. Check directory existence (10 pts)
    if os.path.isdir(deliverables_dir):
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        
    # 2. Check JSON file existence and validity (10 pts)
    report_data = None
    if os.path.isfile(report_file):
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            score_details.append({"item": "检查 board_report.json 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式合法"})
            total_score += 10
        except json.JSONDecodeError:
            score_details.append({"item": "检查 board_report.json 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件存在但非合法 JSON"})
    else:
        score_details.append({"item": "检查 board_report.json 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "board_report.json 文件不存在"})

    # 3. Check data accuracy if JSON is valid (80 pts total)
    if report_data is not None:
        # Metric 1: Cleared volunteer hours = 37.5 (25 pts)
        if find_value_in_json(report_data, 37.5):
            score_details.append({"item": "验证已通过背景调查的志愿者总工时 (37.5)", "score": 25, "max_score": 25, "passed": True, "reason": "工时计算正确"})
            total_score += 25
        else:
            score_details.append({"item": "验证已通过背景调查的志愿者总工时 (37.5)", "score": 0, "max_score": 25, "passed": False, "reason": "未找到正确的工时数值 (37.5)"})
            
        # Metric 2: Total campaign expenses = 3949.5 (25 pts)
        if find_value_in_json(report_data, 3949.5):
            score_details.append({"item": "验证活动总开销精确数值 (3949.5)", "score": 25, "max_score": 25, "passed": True, "reason": "开销总额计算正确"})
            total_score += 25
        else:
            score_details.append({"item": "验证活动总开销精确数值 (3949.5)", "score": 0, "max_score": 25, "passed": False, "reason": "未找到正确的开销总额数值 (3949.50)"})
            
        # Metric 3: Uncleared volunteers list = ["Bob Vance", "Evan Wright"] (30 pts)
        target_list = ["Bob Vance", "Evan Wright"]
        if find_value_in_json(report_data, target_list, is_list=True):
            score_details.append({"item": "验证未通过背景调查的志愿者名单", "score": 30, "max_score": 30, "passed": True, "reason": "名单精确匹配"})
            total_score += 30
        else:
            # Partial check: maybe they provided string instead of list, or missing one
            json_str = json.dumps(report_data)
            has_bob = "Bob Vance" in json_str
            has_evan = "Evan Wright" in json_str
            if has_bob and has_evan:
                score_details.append({"item": "验证未通过背景调查的志愿者名单", "score": 15, "max_score": 30, "passed": False, "reason": "提取到正确名字，但未组织成严格的列表格式"})
                total_score += 15
            else:
                score_details.append({"item": "验证未通过背景调查的志愿者名单", "score": 0, "max_score": 30, "passed": False, "reason": "未能准确列出未通过背调的志愿者全名"})
    else:
        score_details.append({"item": "验证已通过背景调查的志愿者总工时", "score": 0, "max_score": 25, "passed": False, "reason": "无法读取 JSON"})
        score_details.append({"item": "验证活动总开销精确数值", "score": 0, "max_score": 25, "passed": False, "reason": "无法读取 JSON"})
        score_details.append({"item": "验证未通过背景调查的志愿者名单", "score": 0, "max_score": 30, "passed": False, "reason": "无法读取 JSON"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=4)

if __name__ == "__main__":
    verify()
