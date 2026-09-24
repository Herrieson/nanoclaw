import os
import sys
import json
import re
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
    
    def add_score(item, score, max_score, passed, reason):
        nonlocal total_score
        total_score += score
        score_details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    pb_dir = os.path.join(workspace, "project_brief")
    
    # 1. Directory Existence (10 pts)
    if os.path.isdir(pb_dir):
        add_score("创建项目简报目录", 10, 10, True, "目录 `project_brief` 存在")
    else:
        add_score("创建项目简报目录", 0, 10, False, "未找到 `project_brief` 目录")
        # Exit early if no directory, output zero score for the rest implicitly by writing the result.
        write_result(total_score, score_details)
        return

    # Scan files
    files = os.listdir(pb_dir)
    json_file = next((f for f in files if f.endswith(".json")), None)
    chart_file = next((f for f in files if f != json_file and not f.endswith(".json")), None)

    # 2. JSON File Check (10 pts)
    parsed_json = None
    if json_file:
        try:
            with open(os.path.join(pb_dir, json_file), 'r', encoding='utf-8') as f:
                parsed_json = json.load(f)
            add_score("JSON 文件创建及格式合法性", 10, 10, True, f"成功解析 {json_file}")
        except Exception as e:
            add_score("JSON 文件创建及格式合法性", 0, 10, False, f"JSON 解析失败或未找到: {e}")
    else:
        add_score("JSON 文件创建及格式合法性", 0, 10, False, "未找到 JSON 后缀的文件")

    # 3 & 4. JSON Content Exact Match (30 pts)
    if parsed_json is not None:
        json_dump_str = json.dumps(parsed_json)
        
        # 3. Valid items presence (15 pts, 3 pts each)
        valid_ids = ["A01", "A02", "A05", "B02", "B05"]
        found_valid = [vid for vid in valid_ids if vid in json_dump_str]
        valid_score = len(found_valid) * 3
        add_score("JSON 包含正确的合规设备记录", valid_score, 15, len(found_valid) == 5, f"找到合规设备: {found_valid}")
        
        # 4. Invalid items absence (15 pts, 3 pts each)
        invalid_ids = ["A03", "A04", "B01", "B03", "B04"]
        found_invalid = [iid for iid in invalid_ids if iid in json_dump_str]
        invalid_score = (5 - len(found_invalid)) * 3
        add_score("JSON 严格剔除不合规的设备记录", invalid_score, 15, len(found_invalid) == 0, f"发现被误包含的违规设备: {found_invalid if found_invalid else '无'}")
    else:
        add_score("JSON 包含正确的合规设备记录", 0, 15, False, "缺乏有效的 JSON 对象以供提取")
        add_score("JSON 严格剔除不合规的设备记录", 0, 15, False, "缺乏有效的 JSON 对象以供提取")

    # 5. ASCII Chart File Existence and Correct Numbers (15 pts)
    chart_content = ""
    if chart_file:
        try:
            with open(os.path.join(pb_dir, chart_file), 'r', encoding='utf-8') as f:
                chart_content = f.read()
            
            # Totals should be: Solar=550, Wind=300, Hydroponic=170
            has_550 = bool(re.search(r'\b550(?:\.0+)?\b', chart_content))
            has_300 = bool(re.search(r'\b300(?:\.0+)?\b', chart_content))
            has_170 = bool(re.search(r'\b170(?:\.0+)?\b', chart_content))
            
            if has_550 and has_300 and has_170:
                add_score("文本包含准确的分类总成本数值", 15, 15, True, "成功在文本中提取出 550, 300, 170 的聚合成本")
            else:
                add_score("文本包含准确的分类总成本数值", 0, 15, False, f"数值不全。550:{has_550}, 300:{has_300}, 170:{has_170}")
        except Exception as e:
            add_score("文本包含准确的分类总成本数值", 0, 15, False, f"读取图表文件失败: {e}")
    else:
        add_score("文本包含准确的分类总成本数值", 0, 15, False, "未找到图表文本文件")

    # 6. ASCII Chart LLM Validation (20 pts)
    if chart_content.strip():
        llm_prompt = (
            "Determine if the following text is a literal ASCII-style bar chart (or similar visual text chart) "
            "designed to display data on a projector. It should use characters like '|', '-', '*', '#', or block elements "
            "to visually represent lengths corresponding to numerical values. It must NOT be just a plain list or standard text."
        )
        is_ascii_chart = llm_judge_content(llm_prompt, chart_content)
        if is_ascii_chart:
            add_score("利用大模型校验 ASCII 图表格式", 20, 20, True, "大模型判定内容符合 ASCII 条形图特征")
        else:
            add_score("利用大模型校验 ASCII 图表格式", 0, 20, False, "大模型判定内容仅仅是普通文本，并非 ASCII 图表")
    else:
        add_score("利用大模型校验 ASCII 图表格式", 0, 20, False, "图表内容为空或文件不存在")

    write_result(total_score, score_details)

def write_result(total_score, score_details):
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
