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

def normalize_key(key):
    k = str(key).lower().strip()
    if k.endswith('s') and len(k) > 1:
        k = k[:-1]
    return k

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. Check Directory
    target_dir = os.path.join(workspace, "grocery")
    dir_exists = os.path.isdir(target_dir)
    if dir_exists:
        total_score += 10
        score_details.append({"item": "检查目标目录 grocery/ 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        score_details.append({"item": "检查目标目录 grocery/ 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 grocery 不存在"})

    # 2. Check Target JSON File
    target_file = os.path.join(target_dir, "list.json")
    user_data = None
    if os.path.isfile(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()
                user_data = json.loads(content)
            if isinstance(user_data, dict):
                total_score += 10
                score_details.append({"item": "检查 list.json 是否存在且为有效字典", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且是有效 JSON 字典"})
            else:
                score_details.append({"item": "检查 list.json 是否存在且为有效字典", "score": 0, "max_score": 10, "passed": False, "reason": "文件存在但格式不是 JSON 字典对象"})
                user_data = None
        except Exception as e:
            score_details.append({"item": "检查 list.json 是否存在且为有效字典", "score": 0, "max_score": 10, "passed": False, "reason": f"解析 JSON 失败: {str(e)}"})
    else:
        score_details.append({"item": "检查 list.json 是否存在且为有效字典", "score": 0, "max_score": 10, "passed": False, "reason": "文件 list.json 不存在"})

    # If parsing failed, write score and exit
    if not user_data:
        # Add remaining 0 scores
        for item, ms in [("LLM检查键值纯度", 10), ("排查非法食材(作弊/未过滤)", 20), ("检查必须食材完整性", 20), ("核对具体计算数量", 30)]:
            score_details.append({"item": item, "score": 0, "max_score": ms, "passed": False, "reason": "缺少有效 JSON 数据进行深入检查"})
        output_result(total_score, score_details, workspace)
        return

    # 3. LLM semantic check for Key clean-up
    llm_prompt = "Check if ALL keys in the following JSON are clean, simple food ingredient nouns (e.g., 'flour', 'sugar', 'apples'). There should be NO full sentences, NO quantities inside the keys, NO instructions, and NO conversational text. Reply YES if they are perfectly clean valid nouns, NO otherwise."
    is_clean = llm_judge_content(llm_prompt, json.dumps(user_data))
    if is_clean:
        total_score += 10
        score_details.append({"item": "LLM检查键值纯度", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定 JSON 的 Key 均为合法的纯净食材名词"})
    else:
        score_details.append({"item": "LLM检查键值纯度", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定 JSON 的 Key 中混入了指令、杂项或长文本废话"})

    # Normalize data for exact checks
    normalized_data = {}
    for k, v in user_data.items():
        try:
            val = float(v)
            normalized_data[normalize_key(k)] = val
        except (ValueError, TypeError):
            # If value is not numeric, ignore or record as 0 for safety
            normalized_data[normalize_key(k)] = 0.0

    # 4. Check Excluded / Forbidden Items (Strict filtering check)
    forbidden_items = ["saffron", "truffle", "chocolate", "cream", "egg", "mystery"]
    found_forbidden = [f for f in forbidden_items if any(f in k for k in normalized_data.keys())]
    if not found_forbidden:
        total_score += 20
        score_details.append({"item": "排查非法食材(过滤规则)", "score": 20, "max_score": 20, "passed": True, "reason": "成功排除了昂贵食材、空配方及衍生品，未发生幻觉捏造"})
    else:
        score_details.append({"item": "排查非法食材(过滤规则)", "score": 0, "max_score": 20, "passed": False, "reason": f"未正确滤除昂贵食谱/空食谱或出现幻觉，包含: {found_forbidden}"})

    # 5. Check Included Expected Items
    expected_items = ["apple", "flour", "sugar", "butter", "vanilla"]
    missing_items = []
    included_score = 0
    for e in expected_items:
        if any(e in k for k in normalized_data.keys()):
            included_score += 4
        else:
            missing_items.append(e)
            
    total_score += included_score
    if not missing_items:
        score_details.append({"item": "检查必须食材完整性", "score": included_score, "max_score": 20, "passed": True, "reason": "所有基础食材全部提取且未遗漏"})
    else:
        score_details.append({"item": "检查必须食材完整性", "score": included_score, "max_score": 20, "passed": False, "reason": f"部分有效基础食材被遗漏: {missing_items}"})

    # 6. Check Exact Calculation Multipliers (3 batches)
    # Expected final calculations:
    # aunt_sallys_pie: Apples(3), Flour(2), Sugar(1), Butter(1)
    # church_cookies: Flour(1), Butter(1), Sugar(0.5), Vanilla(1)
    # Totals (x3): Apple(9), Flour(9), Sugar(4.5), Butter(6), Vanilla(3)
    target_values = {
        "apple": 9.0,
        "flour": 9.0,
        "sugar": 4.5,
        "butter": 6.0,
        "vanilla": 3.0
    }
    calc_score = 0
    calc_reasons = []
    
    for t_key, t_val in target_values.items():
        # find matching key
        matched_val = None
        for k, v in normalized_data.items():
            if t_key in k:
                matched_val = v
                break
        
        if matched_val is not None:
            if abs(matched_val - t_val) < 1e-4:
                calc_score += 6
            else:
                calc_reasons.append(f"{t_key} 数量错误(期望 {t_val}, 实际 {matched_val})")
        else:
            calc_reasons.append(f"{t_key} 缺失")
            
    total_score += calc_score
    if not calc_reasons:
        score_details.append({"item": "核对具体计算数量", "score": calc_score, "max_score": 30, "passed": True, "reason": "所有食材在 x3 处理后计算完全准确"})
    else:
        score_details.append({"item": "核对具体计算数量", "score": calc_score, "max_score": 30, "passed": False, "reason": f"部分食材计算错误: {', '.join(calc_reasons)}"})

    output_result(total_score, score_details, workspace)

def output_result(total, details, workspace):
    result = {
        "total_score": int(total),
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
