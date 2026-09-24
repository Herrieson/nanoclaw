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
    # 此函数为检测非结构化文本的统一接口
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

def extract_all_string_lists(data):
    """递归提取 JSON 中的所有字符串列表或逗号分隔的字符串内容"""
    lists = []
    if isinstance(data, dict):
        for val in data.values():
            lists.extend(extract_all_string_lists(val))
    elif isinstance(data, list):
        if all(isinstance(x, str) for x in data):
            lists.append([x.lower().strip() for x in data])
        else:
            for val in data:
                lists.extend(extract_all_string_lists(val))
    return lists

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "nursing_station", "shift_prep.json")
    
    score_details = []
    total_score = 0
    
    # 检查项 1：文件和目录是否存在
    if os.path.exists(report_path):
        score_details.append({"item": "检查目标 JSON 报告文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "找到了 shift_prep.json 文件"})
        total_score += 20
    else:
        score_details.append({"item": "检查目标 JSON 报告文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 shift_prep.json 文件"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, ensure_ascii=False, indent=2)
        return

    # 检查项 2：JSON 格式是否合法
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON 格式"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析 JSON 失败: {str(e)}"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, ensure_ascii=False, indent=2)
        return

    extracted_lists = extract_all_string_lists(data)
    # 如果 Agent 把人员作为对象数组给出（比如 {"name": "..."}），进行特殊提取
    if not extracted_lists and isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, list):
                temp_list = []
                for item in val:
                    if isinstance(item, dict) and "name" in item:
                        temp_list.append(item["name"].lower().strip())
                    elif isinstance(item, str):
                        temp_list.append(item.lower().strip())
                if temp_list:
                    extracted_lists.append(temp_list)
    elif not extracted_lists and isinstance(data, list):
        temp_list = []
        for item in data:
            if isinstance(item, dict) and "name" in item:
                temp_list.append(item["name"].lower().strip())
        if temp_list:
            extracted_lists.append(temp_list)

    # 检查项 3：西班牙语教育材料患者列表
    expected_spanish = {"maria garcia", "carlos perez", "luis rodriguez", "rosa martinez"}
    best_spanish_match = 0
    reason_spanish = "未能找到符合预期的西班牙语患者名单"
    for candidate in extracted_lists:
        candidate_set = set(candidate)
        correct_count = len(expected_spanish.intersection(candidate_set))
        false_positives = len(candidate_set - expected_spanish)
        # 精确度打分逻辑
        score = (correct_count * 7) - (false_positives * 5)
        if score > best_spanish_match:
            best_spanish_match = score
            if correct_count == 4 and false_positives == 0:
                reason_spanish = "准确提取了所有需要西班牙语材料的 4 名患者且无多余捏造"
            else:
                reason_spanish = f"提取部分正确: 找到 {correct_count} 人, 误包含 {false_positives} 人"

    best_spanish_match = max(0, min(30, best_spanish_match + (2 if best_spanish_match == 28 else 0))) # round up to 30 if perfect
    if best_spanish_match == 30:
        score_details.append({"item": "提取西班牙语资料需求患者名单", "score": 30, "max_score": 30, "passed": True, "reason": reason_spanish})
    else:
        score_details.append({"item": "提取西班牙语资料需求患者名单", "score": best_spanish_match, "max_score": 30, "passed": False, "reason": reason_spanish})
    total_score += best_spanish_match

    # 检查项 4：饮食限制患者列表
    expected_diet = {"maria garcia", "betty white", "carlos perez", "jane doe", "tom wilson"}
    best_diet_match = 0
    reason_diet = "未能找到符合预期的饮食限制患者名单"
    for candidate in extracted_lists:
        # 跳过看起来像是完全是西班牙语列表的 candidate
        if set(candidate) == expected_spanish and expected_spanish != expected_diet:
            continue
            
        candidate_set = set(candidate)
        correct_count = len(expected_diet.intersection(candidate_set))
        false_positives = len(candidate_set - expected_diet)
        # 精确度打分逻辑 (总分40，每找对1个得8分，错一个扣5分)
        score = (correct_count * 8) - (false_positives * 5)
        if score > best_diet_match:
            best_diet_match = score
            if correct_count == 5 and false_positives == 0:
                reason_diet = "准确提取了所有存在饮食限制的 5 名患者，成功跳过了 Healthy/None，且无多余捏造"
            else:
                reason_diet = f"饮食限制名单提取部分正确: 找到 {correct_count}/5 人, 误包含 {false_positives} 人"

    best_diet_match = max(0, min(40, best_diet_match))
    if best_diet_match == 40:
        score_details.append({"item": "提取带有饮食限制的患者名单", "score": 40, "max_score": 40, "passed": True, "reason": reason_diet})
    else:
        score_details.append({"item": "提取带有饮食限制的患者名单", "score": best_diet_match, "max_score": 40, "passed": False, "reason": reason_diet})
    total_score += best_diet_match

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
