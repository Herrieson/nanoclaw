import os
import sys
import json
import math
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

def find_number_in_json(data, target, tolerance=0.01):
    """递归搜索JSON中是否存在接近target的数值"""
    if isinstance(data, (int, float)):
        if math.isclose(data, target, abs_tol=tolerance):
            return True
    elif isinstance(data, dict):
        return any(find_number_in_json(v, target, tolerance) for v in data.values())
    elif isinstance(data, list):
        return any(find_number_in_json(item, target, tolerance) for item in data)
    return False

def extract_strings_from_json(data):
    """递归提取JSON中的所有字符串"""
    strings = []
    if isinstance(data, str):
        strings.append(data)
    elif isinstance(data, dict):
        for k, v in data.items():
            strings.append(k)
            strings.extend(extract_strings_from_json(v))
    elif isinstance(data, list):
        for item in data:
            strings.extend(extract_strings_from_json(item))
    return strings

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "trip_summary.json")
    
    details = []
    total_score = 0
    
    # Check 1: 报告文件是否存在 (10 分)
    file_exists = os.path.isfile(report_path)
    if file_exists:
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "trip_summary.json 文件存在"})
        total_score += 10
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 reports/trip_summary.json 文件"})
        # 严重错误，提前结束
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 读取文件内容
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content_text = f.read()
            json_data = json.loads(content_text)
        details.append({"item": "检查文件格式是否为合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON 格式"})
        total_score += 10
    except Exception as e:
        details.append({"item": "检查文件格式是否为合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # Check 3: 精准核对总金额计算结果 (40 分)
    # 正确金额为 4*120.50 + 10*15.25 + 3*35.00 + 5*8.75 + 2*22.00 = 827.25
    expected_total = 827.25
    if find_number_in_json(json_data, expected_total):
        details.append({"item": "验证总金额计算正确性", "score": 40, "max_score": 40, "passed": True, "reason": "准确计算并输出了正确的总金额 827.25"})
        total_score += 40
    else:
        details.append({"item": "验证总金额计算正确性", "score": 0, "max_score": 40, "passed": False, "reason": "JSON中未找到正确的总金额数值 (期望: 827.25)，说明解析收据或数学计算失败"})

    # Check 4: 志愿者名单存在性与子集校验 (20 分)
    original_volunteers = ["Mike Smith", "Jenny Lee", "Tom Hanks", "Linda Chen", "Bob Dylan", "Sarah Connor", "David Webb"]
    extracted_strings = extract_strings_from_json(json_data)
    
    found_volunteers = [name for name in original_volunteers if any(name in s for s in extracted_strings)]
    
    if len(found_volunteers) > 0:
        if len(found_volunteers) < len(original_volunteers):
            details.append({"item": "验证志愿者名单是否包含有效子集", "score": 20, "max_score": 20, "passed": True, "reason": f"成功提取了经过过滤的志愿者名单: {found_volunteers}"})
            total_score += 20
        else:
            # 如果全部都在，说明可能没有过滤
            details.append({"item": "验证志愿者名单是否包含有效子集", "score": 10, "max_score": 20, "passed": False, "reason": "JSON中包含了所有志愿者，未进行或未能正确反映资格过滤"})
            total_score += 10
    else:
        details.append({"item": "验证志愿者名单是否包含有效子集", "score": 0, "max_score": 20, "passed": False, "reason": "JSON中没有发现任何原始志愿者姓名，疑似数据丢失或幻觉"})

    # Check 5: LLM 语义检查 - 结构命名与冗余信息判断 (20 分)
    prompt = """Analyze the provided JSON content. Does this JSON explicitly and clearly represent TWO things without any unnecessary conversational fluff:
1. A list (or array) of approved volunteers.
2. A grand total for supply costs.
Return YES if both elements are clearly identifiable by their keys/structure, and NO if it is ambiguous, contains chatty text, or is missing one of the elements."""
    
    llm_passed = llm_judge_content(prompt, content_text)
    if llm_passed:
        details.append({"item": "利用大模型检查语义结构与无冗余性", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定 JSON 结构清晰，包含所需两大要素且无冗余文本"})
        total_score += 20
    else:
        details.append({"item": "利用大模型检查语义结构与无冗余性", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定 JSON 存在语义不明、缺少关键要素或包含多余的自然语言对话"})

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
