import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------- 强制 API 规范 -----------------
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
# ------------------------------------------------

def get_all_values_from_json(obj):
    """递归提取 JSON 中的所有叶子节点值，用于严格判断是否存在目标数据"""
    vals = []
    if isinstance(obj, dict):
        for v in obj.values():
            vals.extend(get_all_values_from_json(v))
    elif isinstance(obj, list):
        for item in obj:
            vals.extend(get_all_values_from_json(item))
    else:
        if isinstance(obj, str):
            vals.append(obj.strip().lower())
        else:
            vals.append(obj)
    return vals

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "contract_winners.json")
    
    score_details = []
    total_score = 0
    
    # Check 1: File Existence
    file_exists = os.path.exists(target_file)
    if file_exists:
        score_details.append({"item": "contract_winners.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建了目标文件"})
        total_score += 10
    else:
        score_details.append({"item": "contract_winners.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2)
        return

    # Check 2: Valid JSON format
    json_data = None
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        score_details.append({"item": "文件为有效 JSON 格式", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "文件为有效 JSON 格式", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return
        
    # 提取所有叶子节点值进行内容验证
    all_values = get_all_values_from_json(json_data)
    
    # Check 3: Plumbing winner (Mario Bros, 12000)
    # Excludes Pipes R Us (Union Dues) and Waterways (more expensive)
    if "mario bros" in all_values and 12000 in all_values:
        if "pipes r us" in all_values:
             score_details.append({"item": "Plumbing 赢家解析", "score": 0, "max_score": 25, "passed": False, "reason": "错误包含了带有敏感词的 Pipes R Us"})
        else:
            score_details.append({"item": "Plumbing 赢家解析", "score": 25, "max_score": 25, "passed": True, "reason": "正确筛选出 Mario Bros 及其总价 12000"})
            total_score += 25
    else:
        score_details.append({"item": "Plumbing 赢家解析", "score": 0, "max_score": 25, "passed": False, "reason": "未找到 Mario Bros 或 价格 12000 缺失/错误"})

    # Check 4: Electrical winner (Sparky's, 9000)
    # Excludes Volt City (Union Dues in line items)
    if "sparky's" in all_values and 9000 in all_values:
        if "volt city" in all_values:
             score_details.append({"item": "Electrical 赢家解析", "score": 0, "max_score": 25, "passed": False, "reason": "错误包含了带有敏感词的 Volt City"})
        else:
            score_details.append({"item": "Electrical 赢家解析", "score": 25, "max_score": 25, "passed": True, "reason": "正确筛选出 Sparky's 及其总价 9000"})
            total_score += 25
    else:
        score_details.append({"item": "Electrical 赢家解析", "score": 0, "max_score": 25, "passed": False, "reason": "未找到 Sparky's 或 价格 9000 缺失/错误"})

    # Check 5: Framing winner (Libertarian Builders, 18000)
    # Excludes Solid Oak Framing (City Permit Tax) and Fast Frame (more expensive)
    if "libertarian builders" in all_values and 18000 in all_values:
        if "solid oak framing" in all_values:
            score_details.append({"item": "Framing 赢家解析", "score": 0, "max_score": 30, "passed": False, "reason": "错误包含了带有敏感词的 Solid Oak Framing"})
        else:
            score_details.append({"item": "Framing 赢家解析", "score": 30, "max_score": 30, "passed": True, "reason": "正确筛选出 Libertarian Builders 及其总价 18000"})
            total_score += 30
    else:
        score_details.append({"item": "Framing 赢家解析", "score": 0, "max_score": 30, "passed": False, "reason": "未找到 Libertarian Builders 或 价格 18000 缺失/错误"})

    # 汇总
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
