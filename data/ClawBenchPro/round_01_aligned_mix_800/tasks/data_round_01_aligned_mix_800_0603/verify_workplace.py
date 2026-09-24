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

def find_numeric_value_by_keyword(data, keyword):
    """Recursively search for a numeric value where the key contains the keyword (case-insensitive)"""
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (int, float)) and keyword in k.lower():
                return v
            elif isinstance(v, (dict, list)):
                res = find_numeric_value_by_keyword(v, keyword)
                if res is not None:
                    return res
    elif isinstance(data, list):
        for item in data:
            res = find_numeric_value_by_keyword(item, keyword)
            if res is not None:
                return res
    return None

def extract_all_strings(data):
    """Recursively extract all strings to check for names"""
    strings = []
    if isinstance(data, dict):
        for k, v in data.items():
            strings.append(str(k))
            strings.extend(extract_all_strings(v))
    elif isinstance(data, list):
        for v in data:
            strings.extend(extract_all_strings(v))
    elif isinstance(data, str):
        strings.append(data)
    return strings

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    deliverables_dir = os.path.join(workspace, "deliverables")
    summary_file = os.path.join(deliverables_dir, "board_summary.json")
    
    # 1. 检查 deliverables 目录
    if os.path.isdir(deliverables_dir):
        score_details.append({"item": "Directory Creation", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables 目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "Directory Creation", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录不存在"})
        
    # 2. 检查 JSON 文件及合法性
    json_data = None
    if os.path.isfile(summary_file):
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            score_details.append({"item": "File Existence & JSON Validity", "score": 15, "max_score": 15, "passed": True, "reason": "board_summary.json 存在且是合法的 JSON"})
            total_score += 15
        except json.JSONDecodeError:
            score_details.append({"item": "File Existence & JSON Validity", "score": 5, "max_score": 15, "passed": False, "reason": "文件存在但非合法 JSON"})
            total_score += 5
    else:
        score_details.append({"item": "File Existence & JSON Validity", "score": 0, "max_score": 15, "passed": False, "reason": "board_summary.json 不存在"})

    # 3 & 4 & 5: 验证数据计算 (Ground truth: Recycling=42, Compost=20, Landfill=15)
    if json_data:
        # Recycling
        recycling_val = find_numeric_value_by_keyword(json_data, "recycling")
        if recycling_val == 42:
            score_details.append({"item": "Accuracy - Recycling Weight", "score": 15, "max_score": 15, "passed": True, "reason": f"成功提取有效学生 Recycling 总计: {recycling_val}"})
            total_score += 15
        else:
            score_details.append({"item": "Accuracy - Recycling Weight", "score": 0, "max_score": 15, "passed": False, "reason": f"Recycling 计算错误，应为 42，实际为 {recycling_val}"})

        # Compost
        compost_val = find_numeric_value_by_keyword(json_data, "compost")
        if compost_val == 20:
            score_details.append({"item": "Accuracy - Compost Weight", "score": 15, "max_score": 15, "passed": True, "reason": f"成功提取有效学生 Compost 总计: {compost_val}"})
            total_score += 15
        else:
            score_details.append({"item": "Accuracy - Compost Weight", "score": 0, "max_score": 15, "passed": False, "reason": f"Compost 计算错误，应为 20，实际为 {compost_val}"})

        # Landfill
        landfill_val = find_numeric_value_by_keyword(json_data, "landfill")
        if landfill_val == 15:
            score_details.append({"item": "Accuracy - Landfill Weight", "score": 15, "max_score": 15, "passed": True, "reason": f"成功提取有效学生 Landfill 总计: {landfill_val}"})
            total_score += 15
        else:
            score_details.append({"item": "Accuracy - Landfill Weight", "score": 0, "max_score": 15, "passed": False, "reason": f"Landfill 计算错误，应为 15，实际为 {landfill_val}"})
            
        # 6. Intruders 验证 (Mason, Sophia) - 不得包含合法学生 (Emma, Liam, Noah, Olivia, Ava)
        all_strs = " ".join(extract_all_strings(json_data)).lower()
        has_mason = "mason" in all_strs
        has_sophia = "sophia" in all_strs
        has_legit = any(name in all_strs for name in ["emma", "liam", "noah", "olivia", "ava"])
        
        if has_mason and has_sophia and not has_legit:
            score_details.append({"item": "Intruders Identification", "score": 30, "max_score": 30, "passed": True, "reason": "精准找到了非法入侵者(Mason, Sophia)且未错误纳入合法名单。"})
            total_score += 30
        elif has_mason or has_sophia:
            score_details.append({"item": "Intruders Identification", "score": 10, "max_score": 30, "passed": False, "reason": "只找到部分入侵者，或者未能干净剔除合法学生名字。"})
            total_score += 10
        else:
            score_details.append({"item": "Intruders Identification", "score": 0, "max_score": 30, "passed": False, "reason": "未能提取入侵者名单。"})
            
    else:
        # 缺失文件，直接补零分项
        score_details.append({"item": "Accuracy - Recycling Weight", "score": 0, "max_score": 15, "passed": False, "reason": "无有效 JSON 数据"})
        score_details.append({"item": "Accuracy - Compost Weight", "score": 0, "max_score": 15, "passed": False, "reason": "无有效 JSON 数据"})
        score_details.append({"item": "Accuracy - Landfill Weight", "score": 0, "max_score": 15, "passed": False, "reason": "无有效 JSON 数据"})
        score_details.append({"item": "Intruders Identification", "score": 0, "max_score": 30, "passed": False, "reason": "无有效 JSON 数据"})

    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
if __name__ == "__main__":
    main()
