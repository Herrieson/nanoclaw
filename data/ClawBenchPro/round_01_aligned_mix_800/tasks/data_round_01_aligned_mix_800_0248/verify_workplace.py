import os
import sys
import json
import httpx
from openai import OpenAI

# 强制 API 规范
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
    target_file = os.path.join(workspace, "reports", "intervention_summary.json")
    
    score_details = []
    total_score = 0
    
    # 1. 检查文件是否存在 (10分)
    if not os.path.exists(target_file):
        score_details.append({"item": "检查目标输出文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "reports/intervention_summary.json 不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2)
        return
    
    score_details.append({"item": "检查目标输出文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    total_score += 10
    
    # 读取内容
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content_str = f.read()
            data = json.loads(content_str)
        score_details.append({"item": "检查JSON格式是否合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "检查JSON格式是否合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 黄金数据 (Golden Data)
    expected_totals = {
        "Alice": 110,
        "Bob": 50,
        "Charlie": 120,
        "David": 75,
        "Eve": 105,
        "Frank": 90
    }
    expected_intervention = {"Bob", "David", "Frank"}
    
    # 2. 解析结构化数据并精准校验 (60分)
    # a. 学生总时长校验
    student_scores = 0
    student_found_names = []
    
    # Agent 可能会用不同的键名包装，我们遍历寻找对应的人名和数值
    # 为了避免死板的键名限制，我们在整个 JSON 的值中搜索
    flat_data = json.dumps(data)
    
    for name, expected_val in expected_totals.items():
        # 严格检查名字是否存在，且对应的值是否正确
        # 这里用纯代码递归寻找该 key 或在列表字典中的匹配
        found_match = False
        def search_dict(d):
            nonlocal found_match
            if isinstance(d, dict):
                # 如果人名作为 key
                for k, v in d.items():
                    if k.lower() == name.lower() and v == expected_val:
                        found_match = True
                    # 如果作为 {'name': 'Alice', 'minutes': 110} 结构
                    if isinstance(v, (int, float)) and v == expected_val and any(name.lower() in str(val).lower() for val in d.values() if isinstance(val, str)):
                        found_match = True
                for v in d.values():
                    search_dict(v)
            elif isinstance(d, list):
                for item in d:
                    search_dict(item)

        search_dict(data)
        if found_match:
            student_scores += 5
            student_found_names.append(name)
            
    if student_scores == 30:
        score_details.append({"item": "校验学生阅读时长计算的准确性(过滤错误状态)", "score": 30, "max_score": 30, "passed": True, "reason": "所有学生的有效时长计算精准（已排除GLITCH和SYNC_ERROR）"})
        total_score += 30
    else:
        score_details.append({"item": "校验学生阅读时长计算的准确性(过滤错误状态)", "score": student_scores, "max_score": 30, "passed": False, "reason": f"部分学生时长计算错误或缺失，仅匹配: {student_found_names}"})
        total_score += student_scores

    # b. 干预名单校验
    intervention_passed = False
    intervention_extracted = set()
    
    # 提取 JSON 中可能是名单的列表（过滤出包含人名的列表）
    def extract_lists(d):
        lists = []
        if isinstance(d, dict):
            for v in d.values():
                lists.extend(extract_lists(v))
        elif isinstance(d, list):
            lists.append(d)
            for item in d:
                lists.extend(extract_lists(item))
        return lists

    all_lists = extract_lists(data)
    for lst in all_lists:
        # 提取列表中的字符串或内部字典的字符串值
        str_items = set()
        for i in lst:
            if isinstance(i, str):
                str_items.add(i)
            elif isinstance(i, dict):
                for v in i.values():
                    if isinstance(v, str):
                        str_items.add(v)
        
        # 检查是否完全匹配 expected_intervention
        matched_names = {n for n in expected_intervention if any(n.lower() in s.lower() for s in str_items)}
        non_intervention = {n for n in expected_totals.keys() if n not in expected_intervention and any(n.lower() in s.lower() for s in str_items)}
        
        if len(matched_names) == 3 and len(non_intervention) == 0:
            intervention_passed = True
            break
            
    if intervention_passed:
        score_details.append({"item": "校验需干预学生名单(少于100分钟)", "score": 30, "max_score": 30, "passed": True, "reason": "干预名单完全准确: Bob, David, Frank"})
        total_score += 30
    else:
        score_details.append({"item": "校验需干预学生名单(少于100分钟)", "score": 0, "max_score": 30, "passed": False, "reason": "干预名单不匹配或包含错误的学生（幻觉或未正确过滤数据）"})

    # 3. LLM 语义与规范校验 (20分)
    # 确保报告中没有泄露任何设备ID（DEV-XXX），并且体现了正确的转换。
    prompt = "Review the provided JSON file content. Does it strictly use actual student names, and completely avoid containing any raw Device IDs like 'DEV-101', 'DEV-202', 'DEV-XXX' anywhere in the output? Answer YES only if there are NO 'DEV-' strings present."
    llm_clean = llm_judge_content(prompt, content_str)
    
    if llm_clean:
        score_details.append({"item": "利用大模型检查是否彻底移除设备ID", "score": 20, "max_score": 20, "passed": True, "reason": "报告中未使用设备ID，完美转换为真实姓名"})
        total_score += 20
    else:
        score_details.append({"item": "利用大模型检查是否彻底移除设备ID", "score": 0, "max_score": 20, "passed": False, "reason": "大模型检测到报告中仍残留或泄露了原始的DEV-ID"})

    # 输出结果
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
