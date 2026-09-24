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

def extract_all_values(data, lists_included=True):
    values = []
    if isinstance(data, dict):
        for v in data.values():
            if lists_included and isinstance(v, list):
                values.append(v)
            values.extend(extract_all_values(v, lists_included))
    elif isinstance(data, list):
        for v in data:
            values.extend(extract_all_values(v, lists_included))
    else:
        values.append(data)
    return values

def check_numeric(values, target, tol=0.01):
    for val in values:
        if isinstance(val, (int, float)):
            if abs(float(val) - target) < tol:
                return True
        elif isinstance(val, str):
            try:
                num = float(val.replace(',', '').replace('$', '').strip())
                if abs(num - target) < tol:
                    return True
            except ValueError:
                pass
    return False

def check_unvetted(values):
    # Mode 1: Array of 2 names
    for val in values:
        if isinstance(val, list) and len(val) == 2:
            lower_list = [str(x).lower() for x in val]
            if any("bob vance" in x for x in lower_list) and any("evan wright" in x for x in lower_list):
                return True
    
    # Mode 2: A single string joining names
    for val in values:
        if isinstance(val, str):
            lower_str = val.lower()
            if "bob vance" in lower_str and "evan wright" in lower_str:
                if "alice hart" not in lower_str and "charlie day" not in lower_str and "diana prince" not in lower_str:
                    return True
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    json_path = os.path.join(deliverables_dir, "board_report.json")
    
    score_details = []
    total_score = 0
    
    # 1. 检查 deliverables 目录
    if os.path.isdir(deliverables_dir):
        total_score += 10
        score_details.append({"item": "目录结构存在", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables 目录已创建"})
    else:
        score_details.append({"item": "目录结构存在", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录未找到"})
        
    # 2. 检查 board_report.json 存在及解析
    json_data = None
    json_str = ""
    if os.path.isfile(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_str = f.read()
                json_data = json.loads(json_str)
            total_score += 15
            score_details.append({"item": "JSON 文件有效性", "score": 15, "max_score": 15, "passed": True, "reason": "board_report.json 是合法的 JSON"})
        except Exception as e:
            score_details.append({"item": "JSON 文件有效性", "score": 0, "max_score": 15, "passed": False, "reason": f"无法解析 JSON: {str(e)}"})
    else:
        score_details.append({"item": "JSON 文件有效性", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 board_report.json 文件"})

    if json_data is not None:
        values = extract_all_values(json_data, lists_included=True)
        
        # 3. 检查 Volunteer Hours == 37.5
        if check_numeric(values, 37.5):
            total_score += 20
            score_details.append({"item": "验证 Cleared 志愿者的精准工时统计", "score": 20, "max_score": 20, "passed": True, "reason": "精准提取出了 37.5"})
        else:
            score_details.append({"item": "验证 Cleared 志愿者的精准工时统计", "score": 0, "max_score": 20, "passed": False, "reason": "未能找到正确的 37.5 总工时"})

        # 4. 检查 Expenses == 3949.5
        if check_numeric(values, 3949.5):
            total_score += 20
            score_details.append({"item": "验证账单脏数据精准相加", "score": 20, "max_score": 20, "passed": True, "reason": "精准提取出了 3949.5 报销总额"})
        else:
            score_details.append({"item": "验证账单脏数据精准相加", "score": 0, "max_score": 20, "passed": False, "reason": "未能找到正确的 3949.5 报销总额"})

        # 5. 检查 Unvetted List 包含且仅包含 Bob Vance, Evan Wright
        if check_unvetted(values):
            total_score += 20
            score_details.append({"item": "识别并筛选未审核人员名单", "score": 20, "max_score": 20, "passed": True, "reason": "成功锁定了 Pending 和 Failed 状态的志愿者列表"})
        else:
            score_details.append({"item": "识别并筛选未审核人员名单", "score": 0, "max_score": 20, "passed": False, "reason": "未审核名单缺失或包含错误人员（只应包含 Bob Vance 和 Evan Wright）"})

        # 6. 利用 LLM 检查 JSON 是否纯净且无过度幻觉
        prompt = "Does the JSON structure have clean, professional, and executive-level keys strictly limited to representing Volunteer Hours, Expenses, and an Unvetted List WITHOUT generating any hallucinated non-profit metrics, unrequested logs, or conversational padding texts?"
        is_clean = llm_judge_content(prompt, json_str)
        if is_clean:
            total_score += 15
            score_details.append({"item": "LLM 语义验证：格式与幻觉检查", "score": 15, "max_score": 15, "passed": True, "reason": "JSON 结构纯净，无无用废话或编造幻觉字段"})
        else:
            score_details.append({"item": "LLM 语义验证：格式与幻觉检查", "score": 0, "max_score": 15, "passed": False, "reason": "大模型判定 JSON 包含冗杂废话、结构不专业或幻觉编造了未要求的字段"})
            
    else:
        # 无法解析 JSON 的级联扣分
        for item in ["验证 Cleared 志愿者的精准工时统计", "验证账单脏数据精准相加", "识别并筛选未审核人员名单", "LLM 语义验证：格式与幻觉检查"]:
            max_p = 20 if "验证" in item or "名单" in item else 15
            score_details.append({"item": item, "score": 0, "max_score": max_p, "passed": False, "reason": "前置条件失败：JSON不可用"})

    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
