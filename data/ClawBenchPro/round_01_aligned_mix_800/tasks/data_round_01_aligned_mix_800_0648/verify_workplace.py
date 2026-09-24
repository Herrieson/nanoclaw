import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """
    非结构化语义验证统一接口
    """
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

def extract_breakdown(data):
    """
    递归提取字典中所有潜在的学生->分钟数映射。
    覆盖了标准的键值对以及 [{"name": "Alice", "minutes": 110}] 这种数组结构。
    """
    found = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (int, float)) and isinstance(k, str):
                found[k] = v
            elif isinstance(v, (dict, list)):
                found.update(extract_breakdown(v))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                keys = list(item.keys())
                strs = [item[k] for k in keys if isinstance(item[k], str)]
                ints = [item[k] for k in keys if isinstance(item[k], (int, float))]
                if len(strs) == 1 and len(ints) == 1:
                    found[strs[0]] = ints[0]
                found.update(extract_breakdown(item))
            elif isinstance(item, list):
                found.update(extract_breakdown(item))
    return found

def find_intervention_match(data, expected_set):
    """
    递归寻找介入名单。支持直接的字符串数组，或是包含准确人名的拼接字符串。
    """
    if isinstance(data, dict):
        for v in data.values():
            if find_intervention_match(v, expected_set): 
                return True
    elif isinstance(data, list):
        if all(isinstance(x, str) for x in data):
            s = {x.strip() for x in data}
            if s == expected_set:
                return True
        for item in data:
            if find_intervention_match(item, expected_set): 
                return True
    elif isinstance(data, str):
        # 兼容逗号拼接形式的字符串："Bob, David, Frank"
        all_students = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"]
        names_in_str = {name for name in all_students if name in data}
        if names_in_str == expected_set:
            return True
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    target_dir = os.path.join(workspace, "reports")
    target_file = os.path.join(target_dir, "intervention_summary.json")
    
    # 【检测1】文件结构合法性 (10分)
    if not os.path.exists(target_file):
        score_details.append({
            "item": "检查目标文件是否存在", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": f"未在 {target_file} 找到文件"
        })
        json_data = None
        content_str = ""
    else:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content_str = f.read()
                json_data = json.loads(content_str)
            score_details.append({
                "item": "检查目标文件是否存在且格式合法", 
                "score": 10, 
                "max_score": 10, 
                "passed": True, 
                "reason": "目标 JSON 文件存在且可正常解析"
            })
            total_score += 10
        except json.JSONDecodeError:
            score_details.append({
                "item": "检查目标文件是否存在且格式合法", 
                "score": 0, 
                "max_score": 10, 
                "passed": False, 
                "reason": "目标文件不是合法的 JSON 格式"
            })
            json_data = None

    if json_data is not None:
        # 【检测2】有效阅读时长统计精确度 (48分，每命中一个学生得8分)
        expected_totals = {
            "Alice": 110, "Bob": 50, "Charlie": 120,
            "David": 75, "Eve": 105, "Frank": 90
        }
        extracted_breakdown = extract_breakdown(json_data)
        correct_count = 0
        missed_students = []
        for student, total in expected_totals.items():
            if extracted_breakdown.get(student) == total:
                correct_count += 1
            else:
                missed_students.append(student)
        
        breakdown_score = correct_count * 8
        total_score += breakdown_score
        score_details.append({
            "item": "精确提取各学生有效阅读总时长",
            "score": breakdown_score,
            "max_score": 48,
            "passed": correct_count == 6,
            "reason": f"正确计算了 {correct_count}/6 个学生。错误/缺失: {', '.join(missed_students) if missed_students else '无'}"
        })

        # 【检测3】干预名单准确性 (30分，严格匹配集合内容)
        expected_intervention = {"Bob", "David", "Frank"}
        if find_intervention_match(json_data, expected_intervention):
            total_score += 30
            score_details.append({
                "item": "过滤并提取干预学生名单 (<100分钟)",
                "score": 30,
                "max_score": 30,
                "passed": True,
                "reason": "成功找到了仅包含 Bob, David 和 Frank 的干预名单"
            })
        else:
            score_details.append({
                "item": "过滤并提取干预学生名单 (<100分钟)",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": "未能找到仅包含 Bob, David 和 Frank 的特定干预名单结构（禁止包含多余名字，也不能少）"
            })

        # 【检测4】利用大模型检查文件的总结正式性 (12分)
        # prompt 明确指出 "formal summary document" 且需要 "clean breakdown" 等。
        prompt_text = (
            "Review the following JSON content. The neurotic teacher requested a 'formal summary document'. "
            "Does this JSON use clear, descriptive keys (e.g., 'student_breakdown', 'intervention_needed', etc.) "
            "and maintain a formal, structured format, rather than just being a raw, unlabelled dump of arrays? "
            "Answer YES if it has clear, descriptive keys and a formal structure."
        )
        is_formal = llm_judge_content(prompt_text, content_str)
        if is_formal:
            total_score += 12
            score_details.append({
                "item": "大模型检查文件结构的正式性",
                "score": 12,
                "max_score": 12,
                "passed": True,
                "reason": "大模型判定 JSON 结构具有良好的描述性 Key，符合正式报告规范"
            })
        else:
            score_details.append({
                "item": "大模型检查文件结构的正式性",
                "score": 0,
                "max_score": 12,
                "passed": False,
                "reason": "大模型判定 JSON 结构缺乏描述性 Key，沦为毫无上下文的原始数据堆砌"
            })

    # 结果落盘
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
