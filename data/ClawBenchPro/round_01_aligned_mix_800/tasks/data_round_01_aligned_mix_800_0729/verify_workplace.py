import os
import sys
import json
import httpx
from openai import OpenAI

# 强制 API 规范
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

def flatten_json_values(obj, values_list=None):
    if values_list is None:
        values_list = []
    if isinstance(obj, dict):
        for val in obj.values():
            flatten_json_values(val, values_list)
    elif isinstance(obj, list):
        for val in obj:
            flatten_json_values(val, values_list)
    else:
        values_list.append(obj)
    return values_list

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    accounting_dir = os.path.join(workspace, "accounting")
    
    score_details = []
    total_score = 0
    
    # 1. Check directory and output file presence (15 points)
    json_files = []
    if os.path.exists(accounting_dir) and os.path.isdir(accounting_dir):
        json_files = [f for f in os.listdir(accounting_dir) if f.endswith(".json")]
        if len(json_files) >= 1:
            score_details.append({"item": "检查 accounting 目录及 JSON 报告存在", "score": 15, "max_score": 15, "passed": True, "reason": "成功找到了 JSON 输出文件"})
            total_score += 15
        else:
            score_details.append({"item": "检查 accounting 目录及 JSON 报告存在", "score": 0, "max_score": 15, "passed": False, "reason": "accounting 目录下没有生成 .json 文件"})
    else:
        score_details.append({"item": "检查 accounting 目录及 JSON 报告存在", "score": 0, "max_score": 15, "passed": False, "reason": "accounting 目录不存在"})
        
    # If no file, fast fail
    if not json_files:
        score_details.append({"item": "JSON 格式合法性校验", "score": 0, "max_score": 15, "passed": False, "reason": "无文件，跳过校验"})
        score_details.append({"item": "校验合格承包商名单", "score": 0, "max_score": 20, "passed": False, "reason": "无文件，跳过校验"})
        score_details.append({"item": "严格校验劳动力总成本 (Labor Cost)", "score": 0, "max_score": 25, "passed": False, "reason": "无文件，跳过校验"})
        score_details.append({"item": "严格校验材料总成本 (Material Cost)", "score": 0, "max_score": 25, "passed": False, "reason": "无文件，跳过校验"})
        write_score(total_score, score_details)
        return
        
    target_file = os.path.join(accounting_dir, json_files[0])
    
    # 2. Check JSON validity (15 points)
    json_data = None
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        score_details.append({"item": "JSON 格式合法性校验", "score": 15, "max_score": 15, "passed": True, "reason": "JSON 解析成功"})
        total_score += 15
    except Exception as e:
        score_details.append({"item": "JSON 格式合法性校验", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON 解析失败：{str(e)}"})
        
    # If not valid JSON, fast fail remaining code-based checks
    if json_data is None:
        score_details.append({"item": "校验合格承包商名单", "score": 0, "max_score": 20, "passed": False, "reason": "非合法 JSON"})
        score_details.append({"item": "严格校验劳动力总成本 (Labor Cost)", "score": 0, "max_score": 25, "passed": False, "reason": "非合法 JSON"})
        score_details.append({"item": "严格校验材料总成本 (Material Cost)", "score": 0, "max_score": 25, "passed": False, "reason": "非合法 JSON"})
        write_score(total_score, score_details)
        return
        
    # Flatten JSON to extract arbitrary structure
    flat_values = flatten_json_values(json_data)
    str_values = [str(v).lower().strip() for v in flat_values]
    num_values = [float(v) for v in flat_values if isinstance(v, (int, float))]
    
    # 3. Check Contractors List (20 points)
    required_contractors = ["apex framing", "desert fox concrete", "baja dirt works", "maverick excavation"]
    rejected_contractors = ["rogue welding", "sloppy joe painters"]
    
    missing = [c for c in required_contractors if not any(c in sv for sv in str_values)]
    included_rejects = [c for c in rejected_contractors if any(c in sv for sv in str_values)]
    
    if len(missing) == 0 and len(included_rejects) == 0:
        score_details.append({"item": "校验合格承包商名单", "score": 20, "max_score": 20, "passed": True, "reason": "准确包含了所有 4 个合格承包商，且未包含 2 个不合格的承包商"})
        total_score += 20
    elif len(included_rejects) > 0:
        score_details.append({"item": "校验合格承包商名单", "score": 0, "max_score": 20, "passed": False, "reason": "包含了因未提交 W-9 而不合格的承包商（如 Rogue Welding 等），发生严重逻辑错误"})
    else:
        score_details.append({"item": "校验合格承包商名单", "score": 0, "max_score": 20, "passed": False, "reason": f"漏掉了合格承包商：{missing}"})
        
    # 4. Check Total Labor Cost (25 points) - Expected: 12600.5
    if 12600.5 in num_values:
        score_details.append({"item": "严格校验劳动力总成本 (Labor Cost)", "score": 25, "max_score": 25, "passed": True, "reason": "成功计算出正确的劳动力总成本 12600.5"})
        total_score += 25
    else:
        score_details.append({"item": "严格校验劳动力总成本 (Labor Cost)", "score": 0, "max_score": 25, "passed": False, "reason": "未能从输出中匹配到正确的计算结果 12600.5"})

    # 5. Check Total Material Cost (25 points) - Expected: 12700.0
    if 12700.0 in num_values or 12700 in num_values:
        score_details.append({"item": "严格校验材料总成本 (Material Cost)", "score": 25, "max_score": 25, "passed": True, "reason": "成功计算出正确的材料总成本 12700.0"})
        total_score += 25
    else:
        score_details.append({"item": "严格校验材料总成本 (Material Cost)", "score": 0, "max_score": 25, "passed": False, "reason": "未能从输出中匹配到正确的计算结果 12700.0"})

    write_score(total_score, score_details)

def write_score(total_score, details):
    output = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    print(f"Evaluation complete. Score: {total_score}/100")

if __name__ == "__main__":
    verify()
