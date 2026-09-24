import os
import sys
import json
import httpx
from openai import OpenAI

# 配置环境
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
    deliverable_path = os.path.join(workspace, "deliverables/eco_summary.json")
    score = 0
    details = []

    # 1. 基础文件存在性检查 (10分)
    if os.path.exists(deliverable_path):
        score += 10
        details.append({"item": "Deliverable file exists", "score": 10, "max_score": 10, "passed": True, "reason": "eco_summary.json found"})
    else:
        details.append({"item": "Deliverable file exists", "score": 0, "max_score": 10, "passed": False, "reason": "eco_summary.json missing"})
        # 写入最终结果并提前退出
        result = {"total_score": 0, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. JSON 格式与基本结构验证 (10分)
    try:
        with open(deliverable_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "JSON structure valid", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON and readable"})
    except Exception as e:
        details.append({"item": "JSON structure valid", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        result = {"total_score": score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 核心计算：Organic Seeds 总数 (30分)
    # 计算逻辑：
    # scribbles.txt: Pumpkin(35) + Tomato(12) = 47
    # inventory_spring.pdf: Tomato(120) + Carrot(85) + Cucumber(40) = 245
    # Total = 292
    expected_seeds = 292
    actual_seeds = data.get("total_organic_seeds") or data.get("total_seeds") # 允许轻微键名差异
    
    if actual_seeds == expected_seeds:
        score += 30
        details.append({"item": "Total Organic Seeds Calculation", "score": 30, "max_score": 30, "passed": True, "reason": f"Correctly identified {expected_seeds} seeds"})
    elif isinstance(actual_seeds, (int, float)) and abs(actual_seeds - expected_seeds) <= 50:
        score += 15
        details.append({"item": "Total Organic Seeds Calculation", "score": 15, "max_score": 30, "passed": False, "reason": f"Partial credit: expected {expected_seeds}, got {actual_seeds}"})
    else:
        details.append({"item": "Total Organic Seeds Calculation", "score": 0, "max_score": 30, "passed": False, "reason": f"Incorrect seed count. Expected {expected_seeds}"})

    # 4. 排序与浇水周期准确性 (30分)
    # 逻辑：必须包含 Pumpkin 并正确调用了 Botanical Skill 获得 3 天。
    # 排序应为：Cucumber(1), Tomato(2), Pumpkin(3), Carrot(4)
    plant_list = data.get("organic_plants", [])
    if isinstance(plant_list, list) and len(plant_list) >= 4:
        # 检查是否包含南瓜及其正确周期（必须通过 Skill 查到是3）
        pumpkin_data = next((p for p in plant_list if "pumpkin" in str(p).lower()), None)
        
        # 检查排序：从频次最高（天数最少）到最低
        days = []
        try:
            for p in plant_list:
                if isinstance(p, dict):
                    d = p.get("watering_interval_days") or p.get("days")
                    if d: days.append(int(d))
            
            is_sorted = all(days[i] <= days[i+1] for i in range(len(days)-1))
            
            if is_sorted and pumpkin_data:
                score += 30
                details.append({"item": "Watering intervals & Sorting", "score": 30, "max_score": 30, "passed": True, "reason": "Plants are correctly sorted and pumpkin data is present"})
            elif is_sorted:
                score += 15
                details.append({"item": "Watering intervals & Sorting", "score": 15, "max_score": 30, "passed": False, "reason": "Sorted correctly but missing key plants or incorrect data points"})
            else:
                details.append({"item": "Watering intervals & Sorting", "score": 0, "max_score": 30, "passed": False, "reason": "List is not sorted by watering frequency"})
        except:
            details.append({"item": "Watering intervals & Sorting", "score": 0, "max_score": 30, "passed": False, "reason": "Could not parse plant list details"})
    else:
        details.append({"item": "Watering intervals & Sorting", "score": 0, "max_score": 30, "passed": False, "reason": "Plant list is missing or insufficient"})

    # 5. 严格过滤非有机植物 (20分)
    # 检查结果中是否包含 GMO_Corn, Pesticide_Soy 或 Chemical weed killers
    forbidden_terms = ["gmo", "pesticide", "chemical", "weed killer"]
    found_forbidden = False
    content_str = json.dumps(data).lower()
    for term in forbidden_terms:
        if term in content_str:
            found_forbidden = True
            break
    
    if not found_forbidden:
        score += 20
        details.append({"item": "Chemical/GMO Exclusion", "score": 20, "max_score": 20, "passed": True, "reason": "No chemical or GMO products found in final list"})
    else:
        details.append({"item": "Chemical/GMO Exclusion", "score": 0, "max_score": 20, "passed": False, "reason": "Found forbidden chemical/GMO items in the output"})

    # 最终输出
    result = {"total_score": score, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
