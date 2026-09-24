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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []

    planning_dir = os.path.join(workspace, "planning")
    json_path = os.path.join(planning_dir, "gps_pins.json")
    md_path = os.path.join(planning_dir, "action_plan.md")

    # 1. Check Directory
    if os.path.isdir(planning_dir):
        total_score += 10
        details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 planning 存在"})
    else:
        details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 planning 不存在"})

    # 2. Check JSON existence and schema
    json_data = None
    if os.path.isfile(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            total_score += 10
            details.append({"item": "检查 gps_pins.json 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "gps_pins.json 存在且是合法的 JSON"})
        except Exception as e:
            details.append({"item": "检查 gps_pins.json 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"gps_pins.json 解析失败: {str(e)}"})
    else:
        details.append({"item": "检查 gps_pins.json 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 gps_pins.json 文件"})

    # 3. Check JSON content logic
    expected_pins = {
        "T-01": 1.2,
        "T-02": 0.5,
        "T-03": 4.1,
        "T-04": 1.1,
        "T-07": 5.5
    }
    
    if json_data is not None and isinstance(json_data, dict):
        score_json_logic = 0
        reasons = []
        parsed_dict = {}
        for k, v in json_data.items():
            try:
                parsed_dict[k] = float(v)
            except:
                pass
        
        # Check expected keys
        matched_keys = 0
        for k, expected_v in expected_pins.items():
            if k in parsed_dict and abs(parsed_dict[k] - expected_v) < 0.01:
                matched_keys += 1
        
        # Determine extra keys
        extra_keys = set(parsed_dict.keys()) - set(expected_pins.keys())
        
        if matched_keys == len(expected_pins) and len(extra_keys) == 0:
            score_json_logic = 40
            reasons.append("数据精准映射，剔除了无效的 KM 和非严重事件。")
        else:
            score_json_logic = matched_keys * 5
            if len(extra_keys) > 0:
                reasons.append(f"包含非法数据（未能正确剔除 invalid/NaN 或者 severity < 8 的项目），发现额外条目 {len(extra_keys)} 个。")
            if matched_keys < len(expected_pins):
                reasons.append(f"遗漏了严重灾害记录。")
            
        passed_json = score_json_logic == 40
        total_score += score_json_logic
        details.append({"item": "检查 gps_pins 结果准确性", "score": score_json_logic, "max_score": 40, "passed": passed_json, "reason": " ".join(reasons)})
    else:
        details.append({"item": "检查 gps_pins 结果准确性", "score": 0, "max_score": 40, "passed": False, "reason": "无合法的字典数据可供验证"})

    # 4. Check action_plan.md existence and structural basics
    md_content = ""
    if os.path.isfile(md_path):
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        if "|" in md_content and "-" in md_content:
            total_score += 10
            details.append({"item": "检查 action_plan.md 文件格式", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建且包含基础表格结构"})
        else:
            details.append({"item": "检查 action_plan.md 文件格式", "score": 5, "max_score": 10, "passed": False, "reason": "文件存在但未检测到标准 markdown 表格符号"})
    else:
        details.append({"item": "检查 action_plan.md 文件格式", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 action_plan.md 文件"})

    # 5. LLM judge for action_plan.md logic
    if md_content:
        prompt_text = (
            "Review the provided action plan. "
            "1. It must contain a table of critical hazards ONLY (Trails: T-01, T-02, T-03, T-04, T-07). "
            "2. It must explicitly mention 'chainsaw' for Fallen Tree issues (T-01, T-04, T-07). "
            "3. It must explicitly mention 'shovels' for Erosion or Mudslide issues (T-02, T-03). "
            "4. It must NOT contain T-05 or T-06 or invalid/NaN kilometer markers. "
            "If all these conditions are strictly met, return YES. Otherwise, return NO."
        )
        is_passed = llm_judge_content(prompt_text, md_content)
        if is_passed:
            total_score += 30
            details.append({"item": "利用大模型检查表格内容和装备推荐逻辑", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定内容包含精准灾害与装备推导"})
        else:
            details.append({"item": "利用大模型检查表格内容和装备推荐逻辑", "score": 0, "max_score": 30, "passed": False, "reason": "大模型判定遗漏灾害或推荐了错误的装备，或包含不应呈现的数据"})
    else:
        details.append({"item": "利用大模型检查表格内容和装备推荐逻辑", "score": 0, "max_score": 30, "passed": False, "reason": "没有 action_plan.md 内容可供评估"})

    score_result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_result, f, indent=2, ensure_ascii=False)
    
    print(f"Validation complete. Total Score: {total_score}")

if __name__ == "__main__":
    main()
