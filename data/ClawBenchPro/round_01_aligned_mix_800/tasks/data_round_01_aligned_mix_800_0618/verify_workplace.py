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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    target_dir = os.path.join(workspace, "nursing_station")
    target_file = os.path.join(target_dir, "shift_prep.json")

    expected_spanish = {"Maria Garcia", "Carlos Perez", "Luis Rodriguez", "Rosa Martinez"}
    expected_dietary = {"Maria Garcia", "Betty White", "Carlos Perez", "Jane Doe", "Tom Wilson"}

    # 1. Check Directory and File Existence
    file_exists = os.path.exists(target_file)
    if file_exists:
        score_details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 shift_prep.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 shift_prep.json 不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. Check JSON Validity
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)
        score_details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON"})
        total_score += 10
    except json.JSONDecodeError:
        score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 解析失败，格式错误"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Helper function to extract all lists of strings from JSON
    extracted_lists = []
    def traverse_json(node):
        if isinstance(node, dict):
            for v in node.values():
                traverse_json(v)
        elif isinstance(node, list):
            if all(isinstance(x, str) for x in node):
                extracted_lists.append(set(x.strip() for x in node))
            else:
                for v in node:
                    traverse_json(v)

    traverse_json(data)

    # 3 & 4. Match Data Lists
    spanish_score = 0
    dietary_score = 0
    spanish_passed = False
    dietary_passed = False
    spanish_reason = "未能找到完全匹配的西班牙语患者名单"
    dietary_reason = "未能找到完全匹配的饮食限制患者名单"

    best_spanish_match = set()
    best_dietary_match = set()

    for lst in extracted_lists:
        # Find best match based on intersection size
        if len(lst & expected_spanish) > len(best_spanish_match & expected_spanish):
            best_spanish_match = lst
        if len(lst & expected_dietary) > len(best_dietary_match & expected_dietary):
            best_dietary_match = lst

    # Evaluate Spanish List (Max 30)
    if best_spanish_match == expected_spanish:
        spanish_score = 30
        spanish_passed = True
        spanish_reason = "成功精准提取所有需要西班牙语材料的患者名单，且无多余冗余数据"
    else:
        missing = expected_spanish - best_spanish_match
        extra = best_spanish_match - expected_spanish
        spanish_score = max(0, 30 - len(missing) * 10 - len(extra) * 10)
        spanish_reason = f"西班牙语患者名单不完全正确。缺失: {missing}, 多余: {extra}。"

    score_details.append({"item": "校验西班牙语患者名单准确性", "score": spanish_score, "max_score": 30, "passed": spanish_passed, "reason": spanish_reason})
    total_score += spanish_score

    # Evaluate Dietary List (Max 30)
    if best_dietary_match == expected_dietary:
        dietary_score = 30
        dietary_passed = True
        dietary_reason = "成功精准提取所有存在饮食限制的患者名单，并正确排除了 'None'，无冗余"
    else:
        missing = expected_dietary - best_dietary_match
        extra = best_dietary_match - expected_dietary
        dietary_score = max(0, 30 - len(missing) * 10 - len(extra) * 10)
        dietary_reason = f"饮食限制患者名单不完全正确。缺失: {missing}, 多余: {extra}。"

    score_details.append({"item": "校验饮食限制患者名单准确性", "score": dietary_score, "max_score": 30, "passed": dietary_passed, "reason": dietary_reason})
    total_score += dietary_score

    # 5. LLM Semantic Validation for Data Structure (Max 20)
    prompt = """
    Please check if this JSON file defines clear, understandable keys (or clear structure) to separate the two requirements: 
    1) Patients needing Spanish medical education materials.
    2) Patients with dietary restrictions.
    Are the keys or structure descriptive enough for a cafeteria worker or nursing staff to understand immediately?
    Answer YES if the structure is clearly understandable and distinct, NO if it's confusing or uses completely generic/obscure keys.
    """
    is_semantic_good = llm_judge_content(prompt, content)
    if is_semantic_good:
        score_details.append({"item": "LLM 语义校验 JSON 结构的易读性", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定 JSON 的 Key 命名及结构具有清晰的业务语义"})
        total_score += 20
    else:
        score_details.append({"item": "LLM 语义校验 JSON 结构的易读性", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定 JSON 结构混乱或 Key 命名未能清晰体现业务意图"})

    # Write output
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
