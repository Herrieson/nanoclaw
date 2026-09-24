import os
import sys
import json
import httpx
import csv
from openai import OpenAI

# 配置常量
EXPECTED_DIR = "deliverables"
EXPECTED_FILE = "ready_volunteers.json"
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, EXPECTED_DIR)
    file_path = os.path.join(deliverables_path, EXPECTED_FILE)
    
    score = 0
    details = []

    # 1. 目录与文件基础存在性检查 (10分)
    if os.path.exists(deliverables_path) and os.path.isdir(deliverables_path):
        score += 5
        details.append({"item": "检查结果目录是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录 deliverables 存在"})
        if os.path.exists(file_path):
            score += 5
            details.append({"item": "检查JSON文件是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件 ready_volunteers.json 存在"})
        else:
            details.append({"item": "检查JSON文件是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 ready_volunteers.json"})
    else:
        details.append({"item": "基础结构检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录"})

    # 2. JSON 格式合法性解析 (10分)
    data = None
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            score += 10
            details.append({"item": "JSON格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 JSON 结构"})
        except Exception as e:
            details.append({"item": "JSON格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})

    # 3. 业务逻辑：年龄过滤 (20分)
    # 规则：年龄 < 16 的必须剔除 (Bobby J 15岁, Hannah Abbott 14岁)
    if data and "volunteers" in data:
        bad_names = ["Bobby J", "Hannah Abbott"]
        found_bad = [v for v in data["volunteers"] if v in bad_names]
        if not found_bad:
            score += 20
            details.append({"item": "年龄过滤(>=16)", "score": 20, "max_score": 20, "passed": True, "reason": "未发现未成年志愿者"})
        else:
            details.append({"item": "年龄过滤(>=16)", "score": 0, "max_score": 20, "passed": False, "reason": f"名单中包含不合格未成年人: {found_bad}"})

    # 4. 业务逻辑：零废弃水瓶验证 (30分)
    # 规则：必须使用 eco_product_validator_skill 验证
    # 合格：Alice (HydroFlask), Diana (Stanley), Evan (Klean Kanteen), Greg (Yeti)
    # 不合格：Charlie (Dasani), Fiona (Poland Spring)
    if data and "volunteers" in data:
        qualified_list = ["Alice Trenton", "Diana Prince", "Evan Wright", "Greg House"]
        disqualified_list = ["Charlie Davis", "Fiona Gallagher"]
        
        current_volunteers = data.get("volunteers", [])
        correct_filtering = all(q in current_volunteers for q in qualified_list) and \
                           all(dq not in current_volunteers for dq in disqualified_list)
        
        if correct_filtering:
            score += 30
            details.append({"item": "水瓶重复使用属性验证", "score": 30, "max_score": 30, "passed": True, "reason": "准确识别并剔除了携带一次性塑料瓶的人员"})
        else:
            details.append({"item": "水瓶重复使用属性验证", "score": 0, "max_score": 30, "passed": False, "reason": "人员名单与水瓶政策要求不符"})

    # 5. 业务逻辑：累计时间计算 (20分)
    # 计算：Alice(4) + Diana(3) + Evan(2) + Greg(4) = 13 小时
    if data and "total_hours" in data:
        try:
            total_hours = float(data["total_hours"])
            if total_hours == 13:
                score += 20
                details.append({"item": "志愿总时长计算", "score": 20, "max_score": 20, "passed": True, "reason": "总时长计算准确 (13小时)"})
            else:
                score += 5
                details.append({"item": "志愿总时长计算", "score": 5, "max_score": 20, "passed": False, "reason": f"时长计算错误，期望13，实际得到 {total_hours}"})
        except:
            details.append({"item": "志愿总时长计算", "score": 0, "max_score": 20, "passed": False, "reason": "无法解析 total_hours 数值"})

    # 6. LLM 审计：数据的完整性与多余字段检查 (10分)
    if data:
        prompt = "Check if the JSON provides a clean list of volunteer names and a single field for total hours. Does it avoid including disqualified people or irrelevant notes?"
        is_clean = llm_judge_content(prompt, json.dumps(data))
        if is_clean:
            score += 10
            details.append({"item": "数据洁净度审计", "score": 10, "max_score": 10, "passed": True, "reason": "LLM 判定产物结构清晰且无无关冗余"})
        else:
            details.append({"item": "数据洁净度审计", "score": 0, "max_score": 10, "passed": False, "reason": "LLM 判定产物包含多余信息或格式不规范"})

    # 输出结果
    output = {
        "total_score": int(score),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
