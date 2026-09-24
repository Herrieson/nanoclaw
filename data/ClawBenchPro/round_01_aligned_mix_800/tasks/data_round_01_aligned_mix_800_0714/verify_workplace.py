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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    # 1. Check directory existence
    if os.path.isdir(deliverables_dir):
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "deliverables 目录存在"})
        total_score += 15
    else:
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "deliverables 目录不存在"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # 2. Check file existence
    files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
    if len(files) > 0:
        score_details.append({"item": "检查 deliverables 目录下是否有文件", "score": 15, "max_score": 15, "passed": True, "reason": f"找到文件: {files[0]}"})
        total_score += 15
    else:
        score_details.append({"item": "检查 deliverables 目录下是否有文件", "score": 0, "max_score": 15, "passed": False, "reason": "deliverables 目录下没有文件"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # Read the first file
    target_file = os.path.join(deliverables_dir, files[0])
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        score_details.append({"item": "读取生成文件", "score": 0, "max_score": 70, "passed": False, "reason": f"无法读取文件: {str(e)}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # Parse content using Regex to extract all order IDs to prevent fuzzing logic on structured data equivalent
    extracted_orders = re.findall(r'ORD-\d{3}', content)
    extracted_orders = list(set(extracted_orders))
    
    # 3. Check Target 1 (ORD-110)
    if "ORD-110" in extracted_orders and "Isabella Cortez" in content:
        score_details.append({"item": "提取目标订单1 (ORD-110)", "score": 20, "max_score": 20, "passed": True, "reason": "正确提取到 ORD-110 及其客户姓名"})
        total_score += 20
    else:
        score_details.append({"item": "提取目标订单1 (ORD-110)", "score": 0, "max_score": 20, "passed": False, "reason": "未能正确提取 ORD-110 或客户姓名缺失"})

    # 4. Check Target 2 (ORD-113)
    if "ORD-113" in extracted_orders and "David Kim" in content:
        score_details.append({"item": "提取目标订单2 (ORD-113)", "score": 20, "max_score": 20, "passed": True, "reason": "正确提取到 ORD-113 及其客户姓名"})
        total_score += 20
    else:
        score_details.append({"item": "提取目标订单2 (ORD-113)", "score": 0, "max_score": 20, "passed": False, "reason": "未能正确提取 ORD-113 或客户姓名缺失"})

    # 5. Exclusion Check (No false positives)
    false_positives = [o for o in ["ORD-111", "ORD-112", "ORD-114"] if o in extracted_orders]
    if len(false_positives) == 0 and len(extracted_orders) <= 2:
        score_details.append({"item": "严格过滤错误数据", "score": 20, "max_score": 20, "passed": True, "reason": "没有包含不符合条件的订单号"})
        total_score += 20
    else:
        score_details.append({"item": "严格过滤错误数据", "score": 0, "max_score": 20, "passed": False, "reason": f"包含错误的订单号或多余捏造字段: {false_positives}"})

    # 6. LLM Check for neatness
    prompt = "Please check if the following file content neatly and clearly presents order numbers and customer names without extraneous clutter. Does it look like a clear summary or list?"
    is_neat = llm_judge_content(prompt, content)
    if is_neat:
        score_details.append({"item": "大模型验证排版清晰度", "score": 10, "max_score": 10, "passed": True, "reason": "排版清晰，可读性好"})
        total_score += 10
    else:
        score_details.append({"item": "大模型验证排版清晰度", "score": 0, "max_score": 10, "passed": False, "reason": "排版混乱，不够清晰简明"})

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
