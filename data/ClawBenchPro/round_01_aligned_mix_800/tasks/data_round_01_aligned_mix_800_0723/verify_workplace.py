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

def extract_all_numbers(data):
    nums = []
    if isinstance(data, dict):
        for k, v in data.items():
            nums.extend(extract_all_numbers(v))
    elif isinstance(data, list):
        for item in data:
            nums.extend(extract_all_numbers(item))
    elif isinstance(data, (int, float)):
        nums.append(data)
    elif isinstance(data, str):
        if data.isdigit():
            nums.append(int(data))
    return nums

def extract_all_lists_of_strings(data):
    lists = []
    if isinstance(data, dict):
        for k, v in data.items():
            lists.extend(extract_all_lists_of_strings(v))
    elif isinstance(data, list):
        is_str_list = all(isinstance(i, str) for i in data) and len(data) > 0
        if is_str_list:
            lists.append(data)
        else:
            for item in data:
                lists.extend(extract_all_lists_of_strings(item))
    return lists

def check_chemical_presence(data):
    text = json.dumps(data).lower()
    forbidden = ["chemical", "gmo_corn", "pesticide_soy", "weed killer"]
    for f in forbidden:
        if f in text:
            return True
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "deliverables", "eco_summary.json")
    
    score_details = []
    total_score = 0
    
    # Check 1: File Existence
    if os.path.exists(target_file):
        score_details.append({"item": "Deliverable 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "eco_summary.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "Deliverable 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "eco_summary.json 未找到"})
        # Write and exit early if no file
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # Check 2: JSON Validity
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({"item": "文件是否为合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 JSON"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "文件是否为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # Check 3: Total Organic Seeds Count
    # Target total = 120 (Tomato CSV) + 85 (Carrot) + 40 (Cucumber) + 35 (Pumpkin TXT) + 12 (Tomato TXT) = 292
    numbers = extract_all_numbers(data)
    if 292 in numbers:
        score_details.append({"item": "总有机种子数量", "score": 30, "max_score": 30, "passed": True, "reason": "精准计算出了 292"})
        total_score += 30
    elif 245 in numbers:
        score_details.append({"item": "总有机种子数量", "score": 10, "max_score": 30, "passed": False, "reason": "计算出了 245，仅解析了 CSV 而遗漏了 TXT"})
        total_score += 10
    elif 47 in numbers:
        score_details.append({"item": "总有机种子数量", "score": 10, "max_score": 30, "passed": False, "reason": "计算出了 47，仅解析了 TXT 而遗漏了 CSV"})
        total_score += 10
    else:
        score_details.append({"item": "总有机种子数量", "score": 0, "max_score": 30, "passed": False, "reason": f"未找到正确总数 292。找到的数字: {numbers}"})

    # Check 4: Organic Plants Watering List Sorted
    # Plants with watering cycle (ascending): Cucumber (1), Tomato (2), Carrot (4)
    # Target list: ["Cucumber", "Tomato", "Carrot"]
    lists = extract_all_lists_of_strings(data)
    list_score = 0
    list_reason = "未找到有效的植物排序列表"
    passed_list = False
    
    for lst in lists:
        lst_lower = [str(x).lower() for x in lst]
        has_cucumber = any("cucumber" in x for x in lst_lower)
        has_tomato = any("tomato" in x for x in lst_lower)
        has_carrot = any("carrot" in x for x in lst_lower)
        has_pumpkin = any("pumpkin" in x for x in lst_lower)
        
        if has_cucumber and has_tomato and has_carrot:
            # Check sorting order
            i_cuc = next(i for i, x in enumerate(lst_lower) if "cucumber" in x)
            i_tom = next(i for i, x in enumerate(lst_lower) if "tomato" in x)
            i_car = next(i for i, x in enumerate(lst_lower) if "carrot" in x)
            
            if i_cuc < i_tom < i_car:
                if has_pumpkin:
                    list_score = 20
                    list_reason = "找到了正确的浇水顺序，但错误地包含了没有浇水周期的 Pumpkin"
                else:
                    list_score = 30
                    list_reason = "准确找到了并按照浇水频率从小到大排序的有机植物列表"
                    passed_list = True
                break
            else:
                list_score = 10
                list_reason = "找全了需要浇水的有机植物，但排序完全错误"
                
    score_details.append({"item": "浇水植物列表及其排序", "score": list_score, "max_score": 30, "passed": passed_list, "reason": list_reason})
    total_score += list_score

    # Check 5: Chemical Excluded
    has_chemical = check_chemical_presence(data)
    if has_chemical:
        score_details.append({"item": "排除化学/转基因植物", "score": 0, "max_score": 20, "passed": False, "reason": "结果中包含应被忽略的化学(Chemical)相关数据或有害植物名字"})
    else:
        score_details.append({"item": "排除化学/转基因植物", "score": 20, "max_score": 20, "passed": True, "reason": "完美排除了所有化学/非有机植物类型"})
        total_score += 20
        
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
