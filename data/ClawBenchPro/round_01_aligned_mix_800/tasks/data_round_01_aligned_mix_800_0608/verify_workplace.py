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

def extract_values(obj):
    """递归提取 JSON 中的所有列表和数值"""
    lists = []
    numbers = []
    strings = []
    if isinstance(obj, dict):
        for v in obj.values():
            l, n, s = extract_values(v)
            lists.extend(l)
            numbers.extend(n)
            strings.extend(s)
    elif isinstance(obj, list):
        lists.append(obj)
        for item in obj:
            l, n, s = extract_values(item)
            lists.extend(l)
            numbers.extend(n)
            strings.extend(s)
    elif isinstance(obj, (int, float)):
        numbers.append(obj)
    elif isinstance(obj, str):
        strings.append(obj)
    return lists, numbers, strings

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "trip_summary.json")
    
    details = []
    total_score = 0
    
    # 1. Check if the required file exists (20 points)
    if os.path.exists(report_path):
        details.append({"item": "检查目标文件 reports/trip_summary.json 是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件已成功生成"})
        total_score += 20
    else:
        details.append({"item": "检查目标文件 reports/trip_summary.json 是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件未生成"})
        
    # 2. Check JSON validity and structure (20 points)
    json_data = None
    if os.path.exists(report_path):
        try:
            with open(report_path, "r") as f:
                content = f.read()
                json_data = json.loads(content)
            details.append({"item": "检查 JSON 格式是否合法", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 解析成功"})
            total_score += 20
        except Exception as e:
            details.append({"item": "检查 JSON 格式是否合法", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
    else:
        details.append({"item": "检查 JSON 格式是否合法", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在，无法解析"})
        
    # 3. Check for exact correct data using heuristic flattening to avoid strict key matching (60 points)
    if json_data is not None:
        lists, numbers, strings = extract_values(json_data)
        
        # Check volunteers (30 points)
        expected_volunteers = {"Mike Smith", "Linda Chen", "Sarah Connor"}
        volunteer_match = False
        
        # Search in lists
        for lst in lists:
            if isinstance(lst, list):
                str_elements = set([str(x).strip() for x in lst if isinstance(x, str)])
                if expected_volunteers.issubset(str_elements) and len(str_elements) == 3:
                    volunteer_match = True
                    break
        
        # Fallback search in strings if agent combined them or saved as a single string
        if not volunteer_match:
            combined_names = " ".join(strings)
            if all(name in combined_names for name in expected_volunteers) and "Tom Hanks" not in combined_names and "Bob Dylan" not in combined_names:
                volunteer_match = True
                
        if volunteer_match:
            details.append({"item": "精确验证合格志愿者名单 (背景调查和急救均通过)", "score": 30, "max_score": 30, "passed": True, "reason": "成功包含且仅包含合格的三名志愿者"})
            total_score += 30
        else:
            details.append({"item": "精确验证合格志愿者名单 (背景调查和急救均通过)", "score": 0, "max_score": 30, "passed": False, "reason": "志愿者名单缺失或包含不合格人员 (未正确剔除 Pending/Fail/No)"})
            
        # Check total costs (30 points)
        # Expected: 4*120.50 + 10*15.25 + 3*35.00 + 5*8.75 + 2*22.00 = 482 + 152.5 + 105 + 43.75 + 44 = 827.25
        expected_cost = 827.25
        cost_match = False
        
        for num in numbers:
            if abs(num - expected_cost) < 0.01:
                cost_match = True
                break
                
        # Fallback to string extraction for numbers
        if not cost_match:
            for s in strings:
                if "827.25" in s:
                    cost_match = True
                    break
                    
        if cost_match:
            details.append({"item": "精确验证物资总花费金额计算准确性", "score": 30, "max_score": 30, "passed": True, "reason": "正确计算出总金额 827.25"})
            total_score += 30
        else:
            details.append({"item": "精确验证物资总花费金额计算准确性", "score": 0, "max_score": 30, "passed": False, "reason": "未能找到正确的总金额计算结果 (预期 827.25)"})
            
    else:
        details.append({"item": "精确验证合格志愿者名单", "score": 0, "max_score": 30, "passed": False, "reason": "JSON 文件缺失，无法验证"})
        details.append({"item": "精确验证物资总花费金额计算准确性", "score": 0, "max_score": 30, "passed": False, "reason": "JSON 文件缺失，无法验证"})

    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
