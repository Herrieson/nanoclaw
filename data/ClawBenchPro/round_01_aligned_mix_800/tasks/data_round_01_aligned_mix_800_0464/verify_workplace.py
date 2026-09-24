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
    
    report_dir = os.path.join(workspace, "final_report")
    json_path = os.path.join(report_dir, "regional_totals.json")
    
    # 1. 检查目录 (10分)
    if os.path.isdir(report_dir):
        score_details.append({"item": "检查 final_report 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 final_report 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        
    # 2. 检查文件 (10分)
    if os.path.isfile(json_path):
        score_details.append({"item": "检查 regional_totals.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 regional_totals.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
    
    # 解析 JSON
    json_data = None
    if os.path.isfile(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            score_details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式合法"})
            total_score += 10
        except json.JSONDecodeError:
            score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "无法解析为有效 JSON"})
    else:
        score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失，跳过"})

    # 结构与数据验证
    expected_data = {
        "West": 4500,
        "North": 12000,
        "South": 2200,
        "Central": 12500,
        "East": 3100
    }
    
    if json_data is not None and isinstance(json_data, dict):
        # 检查是否捏造字段
        extra_keys = set(json_data.keys()) - set(expected_data.keys())
        if extra_keys:
            score_details.append({"item": "检查是否捏造多余区域或字段", "score": 0, "max_score": 20, "passed": False, "reason": f"存在多余字段: {extra_keys}"})
        else:
            # 只有没有多余字段才能拿这20分
            score_details.append({"item": "检查是否捏造多余区域或字段", "score": 20, "max_score": 20, "passed": True, "reason": "未捏造多余字段"})
            total_score += 20
        
        # 逐项检查精准金额 (5个区域，每个10分)
        for region, expected_amount in expected_data.items():
            actual_amount = json_data.get(region)
            if actual_amount == expected_amount:
                score_details.append({"item": f"检查 {region} 区域金额计算是否准确", "score": 10, "max_score": 10, "passed": True, "reason": f"金额匹配: {actual_amount}"})
                total_score += 10
            elif actual_amount is not None:
                score_details.append({"item": f"检查 {region} 区域金额计算是否准确", "score": 0, "max_score": 10, "passed": False, "reason": f"金额不匹配，预期 {expected_amount}，实际 {actual_amount}"})
            else:
                score_details.append({"item": f"检查 {region} 区域金额计算是否准确", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失 {region} 区域数据"})

    elif json_data is not None:
         score_details.append({"item": "检查是否捏造多余区域或字段", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 根节点不是字典"})
         for region in expected_data.keys():
             score_details.append({"item": f"检查 {region} 区域金额计算是否准确", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 结构错误，无法获取对应数据"})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
