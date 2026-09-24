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

def extract_names_from_json(data, target_names):
    """递归提取 JSON 中的目标名字并保持原始顺序"""
    found_names = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(k, str) and k in target_names:
                found_names.append(k)
            if isinstance(v, str) and v in target_names:
                found_names.append(v)
            found_names.extend(extract_names_from_json(v, target_names))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str) and item in target_names:
                found_names.append(item)
            found_names.extend(extract_names_from_json(item, target_names))
    return found_names

def check_value_in_json(data, target_value):
    """递归检查是否存在特定数值"""
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (int, float)) and float(v) == float(target_value):
                return True
            if check_value_in_json(v, target_value):
                return True
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (int, float)) and float(item) == float(target_value):
                return True
            if check_value_in_json(item, target_value):
                return True
    return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    # 1. 检查 suspects.txt (满分 35分)
    suspects_path = os.path.join(workspace, "suspects.txt")
    if not os.path.exists(suspects_path):
        score_details.append({"item": "嫌疑人名单文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "suspects.txt 未生成"})
        score_details.append({"item": "嫌疑人名单内容准确", "score": 0, "max_score": 25, "passed": False, "reason": "文件缺失"})
    else:
        score_details.append({"item": "嫌疑人名单文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "suspects.txt 存在"})
        with open(suspects_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            has_malicious = "malicious user" in content
            has_stranger = "stranger_danger" in content
            
            if has_malicious and has_stranger:
                score_details.append({"item": "嫌疑人名单内容准确", "score": 25, "max_score": 25, "passed": True, "reason": "准确找出了所有的非白名单人员"})
                total_score += 25
            else:
                score_details.append({"item": "嫌疑人名单内容准确", "score": 0, "max_score": 25, "passed": False, "reason": "未找全或内容错误"})
        total_score += 10

    # 2. 检查 deliverables/final_report.json (满分 65分)
    report_path = os.path.join(workspace, "deliverables", "final_report.json")
    if not os.path.exists(report_path):
        score_details.append({"item": "合规报告文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "final_report.json 未生成"})
        score_details.append({"item": "报告格式为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "报告总工时计算精准", "score": 0, "max_score": 25, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "明细列表按名字排序", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失"})
    else:
        score_details.append({"item": "合规报告文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "final_report.json 存在"})
        total_score += 10
        
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            score_details.append({"item": "报告格式为合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "可以正常解析为 JSON 结构"})
            total_score += 10
            
            # 检查总工时是否为 24.0
            if check_value_in_json(report_data, 24.0):
                score_details.append({"item": "报告总工时计算精准", "score": 25, "max_score": 25, "passed": True, "reason": "严格排除了异常数据，得出了 24.0 的正确总工时"})
                total_score += 25
            else:
                score_details.append({"item": "报告总工时计算精准", "score": 0, "max_score": 25, "passed": False, "reason": "工时计算有误，未包含 24.0 或者是幻觉产物"})
                
            # 检查名单排序
            valid_names = ["Alex Chen", "Aria Smith", "Jordan Reed", "Riley Wang", "Casey Taylor"]
            found_names = extract_names_from_json(report_data, valid_names)
            # 剔除重复的，只看唯一出现的先后顺序
            ordered_unique_names = []
            for n in found_names:
                if n not in ordered_unique_names:
                    ordered_unique_names.append(n)
            
            if len(ordered_unique_names) >= 4 and ordered_unique_names == sorted(ordered_unique_names):
                score_details.append({"item": "明细列表按名字排序", "score": 20, "max_score": 20, "passed": True, "reason": "明细中的志愿者姓名按照字母顺序正确排列"})
                total_score += 20
            else:
                score_details.append({"item": "明细列表按名字排序", "score": 0, "max_score": 20, "passed": False, "reason": "名字提取不足或未按字母顺序排列"})
                
        except json.JSONDecodeError:
            score_details.append({"item": "报告格式为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 解析失败，结构损坏"})
            score_details.append({"item": "报告总工时计算精准", "score": 0, "max_score": 25, "passed": False, "reason": "因解析失败无法验证"})
            score_details.append({"item": "明细列表按名字排序", "score": 0, "max_score": 20, "passed": False, "reason": "因解析失败无法验证"})

    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
