import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------------------------------------------------------      
# 配置与初始化
# ----------------------------------------------------------------
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
    report_path = os.path.join(workspace, "front_desk/volunteer_report.json")
    score_details = []
    total_score = 0

    # 1. 检查目录与文件存在性 (10分)
    if os.path.exists(report_path):
        score_details.append({"item": "文件路径检查", "score": 10, "max_score": 10, "passed": True, "reason": "文件 front_desk/volunteer_report.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "文件路径检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 front_desk/volunteer_report.json"})
        # 如果文件不存在，后续检查无法进行，直接写入
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    # 2. 检查 JSON 格式合法性 (10分)
    content = ""
    data = None
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)
        score_details.append({"item": "JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return

    # 3. 核心逻辑：成人名单提取 (40分)
    # 正确成人名单：Sarah(25), Mr. Henderson(60), Emily(40)
    # 应剔除：Little Timmy(12), Jake(17)
    expected_adults = {"Sarah", "Mr. Henderson", "Emily"}
    adult_list = data.get("adult_volunteers", []) if isinstance(data.get("adult_volunteers"), list) else []
    if not adult_list:
        # 兼容性检查：如果是其他字段名
        adult_list = data.get("adults", []) if isinstance(data.get("adults"), list) else []
    
    found_adults = set(adult_list)
    if found_adults == expected_adults:
        score_details.append({"item": "成人名单准确度 (>=18岁)", "score": 40, "max_score": 40, "passed": True, "reason": "完美提取成人名单"})
        total_score += 40
    elif expected_adults.issubset(found_adults) and len(found_adults) > len(expected_adults):
        score_details.append({"item": "成人名单准确度 (>=18岁)", "score": 20, "max_score": 40, "passed": False, "reason": "提取了成人但包含了未成年人(如Little Timmy或Jake)"})
        total_score += 20
    else:
        score_details.append({"item": "成人名单准确度 (>=18岁)", "score": 0, "max_score": 40, "passed": False, "reason": f"名单不匹配。预期 {expected_adults}"})

    # 4. 核心逻辑：总工时计算 (30分)
    # 3 (Timmy) + 4 (Sarah) + 5 (Henderson) + 2 (Jake) + 6 (Emily) = 20
    expected_hours = 20
    actual_hours = data.get("total_hours") or data.get("total_combined_hours")
    
    try:
        actual_hours = float(actual_hours)
        if actual_hours == expected_hours:
            score_details.append({"item": "总工时计算准确度", "score": 30, "max_score": 30, "passed": True, "reason": "总工时计算正确 (20小时)"})
            total_score += 30
        else:
            score_details.append({"item": "总工时计算准确度", "score": 0, "max_score": 30, "passed": False, "reason": f"工时计算错误。预期 20，实际 {actual_hours}"})
    except:
        score_details.append({"item": "总工时计算准确度", "score": 0, "max_score": 30, "passed": False, "reason": "无法在 JSON 中找到有效的 total_hours 数值"})

    # 5. LLM 辅助检查：报告正式度 (10分)
    is_formal = llm_judge_content("Does this JSON report look like a formal report suitable for a director? It should be structured professionally and not contain conversational filler like '*swish swish*' or personal complaints from the transcript.", content)
    if is_formal:
        score_details.append({"item": "报告正式度语义检查", "score": 10, "max_score": 10, "passed": True, "reason": "LLM 判定报告格式正式且无冗余语音噪声"})
        total_score += 10
    else:
        score_details.append({"item": "报告正式度语义检查", "score": 0, "max_score": 10, "passed": False, "reason": "报告内容可能包含未清理的录音杂质或格式极度不正式"})

    # 输出结果
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(total_score), "details": score_details}, f)

if __name__ == "__main__":
    main()
