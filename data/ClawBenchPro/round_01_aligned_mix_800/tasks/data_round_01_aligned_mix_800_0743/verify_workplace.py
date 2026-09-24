import os
import sys
import json
import httpx
import pandas as pd
from openai import OpenAI

# -----------------------------------------------------------------
# 🔒 强制 API 规范与初始化
# -----------------------------------------------------------------
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

# -----------------------------------------------------------------
# 核心验证逻辑
# -----------------------------------------------------------------
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results_dir = os.path.join(workspace, "results")
    output_file = os.path.join(results_dir, "optimal_routes.json")
    score_details = []
    
    # 1. 目录与文件基础结构 (10分)
    dir_exists = os.path.exists(results_dir)
    file_exists = os.path.exists(output_file)
    struct_score = (5 if dir_exists else 0) + (5 if file_exists else 0)
    score_details.append({
        "item": "基础目录与文件存在性",
        "score": struct_score,
        "max_score": 10,
        "passed": dir_exists and file_exists,
        "reason": f"results目录: {dir_exists}, optimal_routes.json: {file_exists}"
    })

    if not file_exists:
        # 如果文件不存在，后续无法进行，直接写入结果
        finalize(score_details)
        return

    # 2. JSON 格式合法性与 Schema 校验 (20分)
    content_data = None
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            content_data = json.load(f)
        
        # 检查是否为预期的 dict 结构
        is_dict = isinstance(content_data, dict)
        valid_schema = True
        if is_dict:
            for k, v in content_data.items():
                if not (isinstance(v, dict) and "total_gain" in v and "max_steepness" in v):
                    valid_schema = False
                    break
        else:
            valid_schema = False
        
        format_score = 20 if valid_schema else 5
        score_details.append({
            "item": "JSON 格式与结构合法性",
            "score": format_score,
            "max_score": 20,
            "passed": valid_schema,
            "reason": "JSON解析成功且包含要求的嵌套字段" if valid_schema else "JSON格式错误或字段缺失"
        })
    except Exception as e:
        score_details.append({
            "item": "JSON 格式与结构合法性",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        finalize(score_details)
        return

    # 3. 核心计算准确性与筛选逻辑 (70分)
    # 正确结果应该是 trail_alpha 和 trail_delta
    # 判定标准：
    # Alpha: Gain 200, Max Steepness 90
    # Delta: Gain 292.5, Max Steepness 95
    # Beta: Gain 600 (Fail)
    # Gamma: Max Steepness 130 (Fail)
    # Epsilon: Gain 80 (Fail)

    expected_trails = {"trail_alpha", "trail_delta"}
    actual_trails = set(content_data.keys())
    
    # A. 筛选正确性 (30分)
    redundant = actual_trails - expected_trails
    missing = expected_trails - actual_trails
    filter_score = 30
    if redundant: filter_score -= 15
    if missing: filter_score -= 15
    filter_score = max(0, filter_score)
    
    score_details.append({
        "item": "路线筛选筛选正确性 (Alpha & Delta)",
        "score": filter_score,
        "max_score": 30,
        "passed": filter_score == 30,
        "reason": f"多余: {redundant}, 缺失: {missing}"
    })

    # B. 数值计算精度 (40分)
    calc_score = 0
    if "trail_alpha" in content_data:
        v = content_data["trail_alpha"]
        if round(float(v.get("total_gain", 0)), 2) == 200.0 and round(float(v.get("max_steepness", 0)), 2) == 90.0:
            calc_score += 20
    if "trail_delta" in content_data:
        v = content_data["trail_delta"]
        if round(float(v.get("total_gain", 0)), 2) == 292.5 and round(float(v.get("max_steepness", 0)), 2) == 95.0:
            calc_score += 20
            
    score_details.append({
        "item": "关键指标计算精度 (Gain & Steepness)",
        "score": calc_score,
        "max_score": 40,
        "passed": calc_score == 40,
        "reason": f"数值匹配得分: {calc_score}/40"
    })

    finalize(score_details)

def finalize(details):
    total_score = sum(d["score"] for d in details)
    result = {
        "total_score": int(total_score),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
