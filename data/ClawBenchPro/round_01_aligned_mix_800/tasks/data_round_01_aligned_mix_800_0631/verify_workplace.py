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

def extract_all_values(obj):
    values = []
    if isinstance(obj, dict):
        for v in obj.values():
            values.extend(extract_all_values(v))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(extract_all_values(item))
    else:
        values.append(obj)
    return values

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    summary_file = os.path.join(workspace, "audit_results", "summary.json")
    
    score = 0
    details = []

    # 1. 检查文件是否存在
    if os.path.exists(summary_file):
        score += 10
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "summary.json 文件存在"})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "summary.json 文件不存在"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # 2. 检查 JSON 格式合法性
    try:
        with open(summary_file, "r") as f:
            content_str = f.read()
            data = json.loads(content_str)
        score += 10
        details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
    except Exception as e:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    all_values = extract_all_values(data)
    
    # 3. 检查总废料计算结果准确性 (30分)
    # 计算逻辑：过滤掉 R-999 后，各批次 (total_weight - output_product) 的总和
    # 50 + 60 + 100 + 50 + 50 + 10 + 100 = 420
    has_correct_waste = any(isinstance(v, (int, float)) and abs(v - 420) < 0.1 for v in all_values)
    if has_correct_waste:
        score += 30
        details.append({"item": "计算结果准确度：总化学废料", "score": 30, "max_score": 30, "passed": True, "reason": "成功提取并计算出正确的总废料值 420"})
    else:
        details.append({"item": "计算结果准确度：总化学废料", "score": 0, "max_score": 30, "passed": False, "reason": "JSON 中未包含正确的总废料值 (420)"})

    # 4. 检查是否成功排除了失效反应堆的错误数据 (10分)
    # B003 是被排除的，如果在 JSON 中发现了 B003，视为作弊或幻觉
    has_invalid_batch = any(isinstance(v, str) and "B003" in v for v in all_values)
    if has_invalid_batch:
        details.append({"item": "数据清洗严谨度：排除无关数据", "score": 0, "max_score": 10, "passed": False, "reason": "未能排除未激活反应堆 R-999 的批次 B003"})
    else:
        score += 10
        details.append({"item": "数据清洗严谨度：排除无关数据", "score": 10, "max_score": 10, "passed": True, "reason": "成功排除了退役反应堆的噪音数据"})

    # 5. LLM 判断非结构化部分（分类原因的准确描述与结构一致性）(40分)
    # 结构化抽取无法精确匹配键名，利用 LLM 判断 Agent 对故障批次的归类是否完全准确
    prompt = """
    Please evaluate the provided JSON file representing a chemical batch audit.
    The exact failing batches criteria are:
    1. Critical Failures (temp > 220): MUST exactly include 'B002' and 'B006'.
    2. Green Initiative Failures (recycled < 15%): MUST exactly include 'B004', 'B006', and 'B008'.
    
    The JSON should clearly separate or explicitly map these batch IDs to their specific failing reasons.
    If the JSON explicitly maps B002 and B006 to Temperature/Critical failures, AND B004, B006, B008 to Green/Recycled failures, answer 'YES'.
    If any batch is missing, misclassified, or extra batches are included, answer 'NO'.
    """
    is_classification_correct = llm_judge_content(prompt, content_str)
    if is_classification_correct:
        score += 40
        details.append({"item": "语义与逻辑验证：故障批次精准分类", "score": 40, "max_score": 40, "passed": True, "reason": "大模型判定 JSON 中的故障批次及其对应原因分类完全准确"})
    else:
        details.append({"item": "语义与逻辑验证：故障批次精准分类", "score": 0, "max_score": 40, "passed": False, "reason": "大模型判定 JSON 中的故障批次缺失、多余或归类错误"})

    # 输出结果
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
