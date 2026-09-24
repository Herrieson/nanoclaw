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
                {"role": "user", "content": f"{prompt_text}\n\n[Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def extract_all_values(data):
    """Recursively extract all string values from a JSON object."""
    values = []
    if isinstance(data, dict):
        for v in data.values():
            values.extend(extract_all_values(v))
    elif isinstance(data, list):
        for item in data:
            values.extend(extract_all_values(item))
    elif isinstance(data, str):
        values.append(data)
    return values

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # 1. 检查 deliverables 目录
    dir_exists = os.path.isdir(deliverables_dir)
    if dir_exists:
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录"})
        
    if not dir_exists:
        # 无法继续
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. 检查 JSON 文件存在并格式合法
    json_files = [f for f in os.listdir(deliverables_dir) if f.endswith(".json")]
    valid_json_data = None
    if len(json_files) == 1:
        score_details.append({"item": "存在唯一 JSON 输出文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到文件 {json_files[0]}"})
        total_score += 10
        try:
            with open(os.path.join(deliverables_dir, json_files[0]), "r", encoding="utf-8") as f:
                valid_json_data = json.load(f)
            score_details.append({"item": "JSON 格式合法解析", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件可以成功解析"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "JSON 格式合法解析", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
    elif len(json_files) > 1:
        score_details.append({"item": "存在唯一 JSON 输出文件", "score": 0, "max_score": 10, "passed": False, "reason": "存在多于一个 JSON 文件，没有做到 flawless tidy"})
        # 尝试取第一个解析
        try:
            with open(os.path.join(deliverables_dir, json_files[0]), "r", encoding="utf-8") as f:
                valid_json_data = json.load(f)
        except:
            pass
    else:
        score_details.append({"item": "存在唯一 JSON 输出文件", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 JSON 文件"})
        score_details.append({"item": "JSON 格式合法解析", "score": 0, "max_score": 10, "passed": False, "reason": "无文件可解析"})
        
    # 3. 检查具体内容
    if valid_json_data is not None:
        all_str_values = extract_all_values(valid_json_data)
        merged_values = " ".join(all_str_values).upper()
        
        # 颜色检查
        colors_to_find = ["#1A5276", "#F1C40F", "#333333"]
        found_colors = 0
        for color in colors_to_find:
            if color in merged_values:
                found_colors += 1
                
        color_score = found_colors * 10
        total_score += color_score
        score_details.append({
            "item": "准确提取 Project Aura 的 Hex Codes", 
            "score": color_score, 
            "max_score": 30, 
            "passed": color_score == 30, 
            "reason": f"找到了 {found_colors}/3 个要求的颜色"
        })
        
        # 检查是否掺杂了老项目的颜色
        if "#FFFFFF" in merged_values or "#000000" in merged_values:
            score_details.append({
                "item": "剔除 Project Veda 噪音数据", 
                "score": 0, 
                "max_score": 10, 
                "passed": False, 
                "reason": "输出了被废弃的 Veda 项目颜色"
            })
        else:
            score_details.append({
                "item": "剔除 Project Veda 噪音数据", 
                "score": 10, 
                "max_score": 10, 
                "passed": True, 
                "reason": "未发现 Veda 项目的废弃颜色"
            })
            total_score += 10
            
        # 提取使命宣言，并使用大模型验证语义
        # 合并所有文本，检查是否包含正确的mission statement意思
        prompt = "Does the following content contain a mission statement that means exactly 'Empowering digital communities through intuitive scalable web solutions.'? Ignore the case and minor punctuation differences, but the core meaning and main words MUST match."
        llm_pass = llm_judge_content(prompt, " ".join(all_str_values))
        
        if llm_pass:
            score_details.append({
                "item": "提取准确的 Mission Statement", 
                "score": 30, 
                "max_score": 30, 
                "passed": True, 
                "reason": "LLM 验证 mission statement 语义准确"
            })
            total_score += 30
        else:
            score_details.append({
                "item": "提取准确的 Mission Statement", 
                "score": 0, 
                "max_score": 30, 
                "passed": False, 
                "reason": "LLM 验证未能找到准确的 mission statement"
            })
    else:
        # 无数据则后续得零分
        score_details.append({"item": "准确提取 Project Aura 的 Hex Codes", "score": 0, "max_score": 30, "passed": False, "reason": "没有有效的 JSON 数据"})
        score_details.append({"item": "剔除 Project Veda 噪音数据", "score": 0, "max_score": 10, "passed": False, "reason": "没有有效的 JSON 数据"})
        score_details.append({"item": "提取准确的 Mission Statement", "score": 0, "max_score": 30, "passed": False, "reason": "没有有效的 JSON 数据"})
        
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
