import os
import sys
import json
import httpx
from openai import OpenAI

# 环境变量配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """检测非结构化文本的统一接口"""
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

def extract_all_strings(data):
    """递归提取 JSON 中的所有字符串内容以供验证"""
    strings = []
    if isinstance(data, dict):
        for k, v in data.items():
            strings.append(str(k))
            strings.extend(extract_all_strings(v))
    elif isinstance(data, list):
        for item in data:
            strings.extend(extract_all_strings(item))
    elif isinstance(data, str):
        strings.append(data)
    else:
        strings.append(str(data))
    return strings

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = os.path.join(workspace, "output")
    action_plan_path = os.path.join(output_dir, "action_plan.json")
    hazard_chart_path = os.path.join(output_dir, "hazard_chart.txt")
    
    details = []
    total_score = 0

    # 1. 检查输出目录 (10分)
    if os.path.isdir(output_dir):
        details.append({"item": "检查 output 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "output 目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查 output 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "output 目录缺失"})
        
    # 2. 检查 JSON 文件格式合法性 (10分)
    json_valid = False
    json_data = None
    if os.path.exists(action_plan_path):
        try:
            with open(action_plan_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            json_valid = True
            details.append({"item": "检查 action_plan.json 是否为合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式解析成功"})
            total_score += 10
        except Exception as e:
            details.append({"item": "检查 action_plan.json 是否为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
    else:
        details.append({"item": "检查 action_plan.json 是否为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "action_plan.json 文件不存在"})

    # 3. 检查结构化数据：正确筛选路线和志愿者，无幻觉数据 (共 30 分)
    if json_valid and json_data:
        all_text = " ".join(extract_all_strings(json_data)).lower()
        
        # 3.1 危险路线筛选 (15分)
        # Hazard > 3 的路线: Bear Creek, Summit Path, Canyon Descent
        expected_trails = ["bear creek", "summit path", "canyon descent"]
        wrong_trails = ["pine ridge", "lake loop", "meadow trail"]
        
        has_all_expected_trails = all(t in all_text for t in expected_trails)
        has_no_wrong_trails = not any(wt in all_text for wt in wrong_trails)
        
        if has_all_expected_trails and has_no_wrong_trails:
            details.append({"item": "检查危险路线清单提取准确性", "score": 15, "max_score": 15, "passed": True, "reason": "成功提取所有危险路线且没有包含安全路线"})
            total_score += 15
        else:
            reason = "危险路线清单包含错误路线或缺失应该包含的路线。"
            details.append({"item": "检查危险路线清单提取准确性", "score": 0, "max_score": 15, "passed": False, "reason": reason})

        # 3.2 志愿者筛选 (15分)
        # 包含 clearing 技能的志愿者: Samuel, Marie
        expected_vols = ["samuel", "marie"]
        wrong_vols = ["david", "chloe", "jerome"]
        
        has_all_expected_vols = all(v in all_text for v in expected_vols)
        has_no_wrong_vols = not any(wv in all_text for wv in wrong_vols)
        
        if has_all_expected_vols and has_no_wrong_vols:
            details.append({"item": "检查合格志愿者清单提取准确性", "score": 15, "max_score": 15, "passed": True, "reason": "成功提取具备 clearing 技能的志愿者且无多余人员"})
            total_score += 15
        else:
            reason = "志愿者清单包含不合格人员或遗漏了具备能力的人员。"
            details.append({"item": "检查合格志愿者清单提取准确性", "score": 0, "max_score": 15, "passed": False, "reason": reason})
    else:
        details.append({"item": "检查危险路线清单提取准确性", "score": 0, "max_score": 15, "passed": False, "reason": "JSON不合法，无法验证数据"})
        details.append({"item": "检查合格志愿者清单提取准确性", "score": 0, "max_score": 15, "passed": False, "reason": "JSON不合法，无法验证数据"})

    # 4. 检查图表文件是否存在 (20分)
    chart_content = ""
    if os.path.exists(hazard_chart_path):
        try:
            with open(hazard_chart_path, 'r', encoding='utf-8') as f:
                chart_content = f.read()
            if len(chart_content.strip()) > 10:
                details.append({"item": "检查 hazard_chart.txt 图表文件生成", "score": 20, "max_score": 20, "passed": True, "reason": "图表文件生成且有实质内容"})
                total_score += 20
            else:
                details.append({"item": "检查 hazard_chart.txt 图表文件生成", "score": 0, "max_score": 20, "passed": False, "reason": "图表文件为空或内容过少"})
        except Exception as e:
            details.append({"item": "检查 hazard_chart.txt 图表文件生成", "score": 0, "max_score": 20, "passed": False, "reason": f"读取失败: {str(e)}"})
    else:
         details.append({"item": "检查 hazard_chart.txt 图表文件生成", "score": 0, "max_score": 20, "passed": False, "reason": "图表文件未生成"})

    # 5. LLM 大模型验证 ASCII 图表内容正确性 (30分)
    if chart_content:
        prompt_text = (
            "Does the following file content represent an ASCII bar chart? "
            "It must clearly show the hazard levels of specifically these three trails: "
            "Bear Creek (level 5), Summit Path (level 4), and Canyon Descent (level 6). "
            "If it visually represents these lengths/levels with text characters (like '*', '-', '#', etc.), "
            "and does NOT include other non-dangerous trails, output YES, otherwise output NO."
        )
        is_valid_chart = llm_judge_content(prompt_text, chart_content)
        if is_valid_chart:
            details.append({"item": "LLM 语义验证 ASCII 图表准确性", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定 ASCII 柱状图格式正确且数据映射无误"})
            total_score += 30
        else:
            details.append({"item": "LLM 语义验证 ASCII 图表准确性", "score": 0, "max_score": 30, "passed": False, "reason": "大模型认为图表未正确反映指定的危险等级数据或包含了错误信息"})
    else:
        details.append({"item": "LLM 语义验证 ASCII 图表准确性", "score": 0, "max_score": 30, "passed": False, "reason": "缺少图表文件，无法验证"})

    # 结果输出
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
