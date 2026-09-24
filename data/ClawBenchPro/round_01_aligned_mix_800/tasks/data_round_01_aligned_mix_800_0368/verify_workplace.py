import os
import sys
import json
import glob
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

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
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # 1. Check Directory
    if os.path.isdir(deliverables_dir):
        total_score += 10
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已创建"})
    else:
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录"})
        return dump_result(total_score, score_details)

    # 2. Check JSON file existence
    json_files = glob.glob(os.path.join(deliverables_dir, "*.json"))
    if json_files:
        total_score += 10
        score_details.append({"item": "检查是否生成了 JSON 产物文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到文件: {os.path.basename(json_files[0])}"})
    else:
        score_details.append({"item": "检查是否生成了 JSON 产物文件", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录下没有 JSON 文件"})
        return dump_result(total_score, score_details)

    target_file = json_files[0]
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content_str = f.read()
            data = json.loads(content_str)
    except Exception as e:
        score_details.append({"item": "JSON 文件解析与结构合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"无法解析 JSON 文件: {str(e)}"})
        return dump_result(total_score, score_details)

    total_score += 10
    score_details.append({"item": "JSON 文件解析与基础结构合法性", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON 格式"})

    # 3. Exact Count Verification
    # Expected matches: ID_881, ID_883, ID_885, ID_887 -> Total 4
    has_correct_count = False
    count_val = None
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, int) and v == 4:
                has_correct_count = True
                count_val = v
                break

    if has_correct_count:
        total_score += 20
        score_details.append({"item": "提取条目数量精确验证", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取且精准统计了4条符合条件的反馈"})
    else:
        score_details.append({"item": "提取条目数量精确验证", "score": 0, "max_score": 20, "passed": False, "reason": "未找到正确的统计数值（应为 4）"})

    # 4. Data Accuracy Verification
    expected_matches = {
        "Alice Smith": "The store needs more diversity in its product lines.",
        "Bob Lee": "The wheelchair ramp is blocked by the new display. Terrible Accessibility.",
        "David Kim": "I loved the cultural diversity event last week!",
        "George Miller": "Accessibility to the restrooms is severely lacking."
    }
    
    found_matches = 0
    list_data = None
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                list_data = v
                break
    elif isinstance(data, list):
        list_data = data

    if list_data:
        for item in list_data:
            item_str = json.dumps(item)
            for exp_name, exp_comment in expected_matches.items():
                if exp_name in item_str and exp_comment in item_str:
                    found_matches += 1
                    break
        
        # Penalize for hallucinations or raw IDs
        has_hallucination = "ID_" in json.dumps(list_data)
        
        if found_matches == 4 and not has_hallucination:
            total_score += 40
            score_details.append({"item": "数据精准映射与去敏转换", "score": 40, "max_score": 40, "passed": True, "reason": "精准包含了全部4位真实姓名及对应评论，且未遗留未转换的 customer_id"})
        elif found_matches > 0:
            partial_score = found_matches * 5
            total_score += partial_score
            score_details.append({"item": "数据精准映射与去敏转换", "score": partial_score, "max_score": 40, "passed": False, "reason": f"仅匹配了 {found_matches}/4 条数据，或遗留了原版 ID"})
        else:
            score_details.append({"item": "数据精准映射与去敏转换", "score": 0, "max_score": 40, "passed": False, "reason": "未能将客户 ID 正确映射为姓名并关联评论"})
    else:
        score_details.append({"item": "数据精准映射与去敏转换", "score": 0, "max_score": 40, "passed": False, "reason": "未找到包含反馈条目的列表结构"})

    # 5. LLM Professionalism Validation
    prompt = "Does the following JSON structure use professional, well-named keys (e.g., 'total_count', 'feedbacks', 'customer_name', 'comment') and look like a clean deliverable for corporate reporting? Answer YES if it looks highly professional without random or sloppy key names."
    is_professional = llm_judge_content(prompt, content_str)
    if is_professional:
        total_score += 10
        score_details.append({"item": "JSON 结构与字段命名的专业性 (LLM评估)", "score": 10, "max_score": 10, "passed": True, "reason": "LLM 判定字段命名专业、结构清晰"})
    else:
        score_details.append({"item": "JSON 结构与字段命名的专业性 (LLM评估)", "score": 0, "max_score": 10, "passed": False, "reason": "LLM 判定结构杂乱或字段命名不规范"})

    return dump_result(total_score, score_details)

def dump_result(total_score, details):
    res = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
