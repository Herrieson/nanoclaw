import os
import sys
import json
import glob
import httpx
from openai import OpenAI

# =====================================================================
# 强制要求的 LLM API 规范
# =====================================================================
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型专门用于非结构化语义和逻辑常识验证"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[Content to verify]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

# =====================================================================
# 辅助工具函数
# =====================================================================
def get_client_record(parsed_data, target_name):
    """处理 Agent 各种可能的 JSON 嵌套层级，精准提取特定客户的数据记录"""
    if isinstance(parsed_data, list):
        for item in parsed_data:
            if isinstance(item, dict):
                for k, v in item.items():
                    if isinstance(v, str) and target_name.lower() in v.lower():
                        return item
    elif isinstance(parsed_data, dict):
        for k, v in parsed_data.items():
            if target_name.lower() in k.lower():
                return v
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    if isinstance(sub_v, str) and target_name.lower() in sub_v.lower():
                        return v
    return None

def find_value_by_keywords(record, keywords):
    """容错提取字段，应对 Agent 自主命名的 key"""
    if not isinstance(record, dict): return None
    for k, v in record.items():
        if any(kw.lower() in k.lower() for kw in keywords):
            return v
    return None

# =====================================================================
# 主验证逻辑
# =====================================================================
def verify_workplace(workspace_dir):
    details = []
    total_score = 0
    
    party_prep_dir = os.path.join(workspace_dir, "party_prep")
    
    # [Check 1: 目录结构验证 (10 分)]
    if os.path.isdir(party_prep_dir):
        json_files = glob.glob(os.path.join(party_prep_dir, "*.json"))
        if json_files:
            details.append({"item": "检查目标目录及JSON文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"成功找到 {json_files[0]}"})
            total_score += 10
            target_json = json_files[0]
        else:
            details.append({"item": "检查目标目录及JSON文件是否存在", "score": 5, "max_score": 10, "passed": False, "reason": "party_prep 目录存在，但未找到 JSON 文件"})
            total_score += 5
            target_json = None
    else:
        details.append({"item": "检查目标目录及JSON文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "party_prep 目录未创建"})
        target_json = None

    if not target_json:
        return total_score, details

    # [Check 2: 文件格式校验与 Schema 解析 (10 分)]
    parsed_data = None
    try:
        with open(target_json, 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)
        details.append({"item": "检查文件格式是否符合 JSON 标准", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件成功解析"})
        total_score += 10
    except Exception as e:
        details.append({"item": "检查文件格式是否符合 JSON 标准", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        return total_score, details

    # 标准答案数据
    expected_calories = {
        "Alice": 1269,  # Spin: 729 + Core: 540
        "Bob": 540,     # Yoga: 540
        "Charlie": 594, # HIIT: 594
        "David": 720,   # Spin: 720
        "Eve": 630      # Pilates: 630
    }
    attendees = {"Alice": "Kosher", "Charlie": "Vegan", "David": "Gluten-Free"}
    non_attendees = ["Bob", "Eve"]

    # [Check 3: 卡路里计算精准度验证 (30 分，每个用户 6 分)]
    # Agent 必须调用 v2 API 才能算出此分数，直接用公式计算极大概率不一致
    cal_score = 0
    cal_failed = []
    for user, expected_cal in expected_calories.items():
        record = get_client_record(parsed_data, user)
        if record:
            cal_val = find_value_by_keywords(record, ["calorie", "cal", "burn"])
            try:
                if cal_val is not None and int(cal_val) == expected_cal:
                    cal_score += 6
                else:
                    cal_failed.append(f"{user}(期望:{expected_cal}, 实际:{cal_val})")
            except:
                cal_failed.append(f"{user}(数值异常)")
        else:
            cal_failed.append(f"{user}(记录缺失)")
    
    if not cal_failed:
        details.append({"item": "精确验证各用户总卡路里数值 (必须通过v2计算器)", "score": 30, "max_score": 30, "passed": True, "reason": "所有 5 名用户的卡路里完全准确"})
    else:
        details.append({"item": "精确验证各用户总卡路里数值", "score": cal_score, "max_score": 30, "passed": False, "reason": f"错误或缺失的用户: {', '.join(cal_failed)}"})
    total_score += cal_score

    # [Check 4: 饮食禁忌与 RSVP 逻辑过滤验证 (20 分)]
    # 要求：参加者必须有diet信息，未参加者必须没有或为Null/False
    logic_score = 0
    logic_errors = []
    
    # 验证非出席者
    for user in non_attendees:
        record = get_client_record(parsed_data, user)
        if record:
            diet = find_value_by_keywords(record, ["diet", "restriction"])
            snack = find_value_by_keywords(record, ["snack", "recommend"])
            if diet or snack:
                logic_errors.append(f"{user}(未RSVP却生成了禁忌/零食信息)")
            else:
                logic_score += 4
        else:
            logic_errors.append(f"{user}(记录被完全丢弃，未保留卡路里信息)")
            
    # 验证出席者
    for user in attendees.keys():
        record = get_client_record(parsed_data, user)
        if record:
            diet = find_value_by_keywords(record, ["diet", "restriction"])
            if diet and str(attendees[user]).lower() in str(diet).lower():
                logic_score += 4
            else:
                logic_errors.append(f"{user}(缺失禁忌或禁忌错误)")
        else:
            logic_errors.append(f"{user}(记录缺失)")

    if logic_score == 20:
        details.append({"item": "验证出席者过滤逻辑", "score": 20, "max_score": 20, "passed": True, "reason": "逻辑完美，严格剔除了未参加者的零食与饮食数据，保留了全部卡路里基础信息"})
    else:
        details.append({"item": "验证出席者过滤逻辑", "score": logic_score, "max_score": 20, "passed": False, "reason": f"逻辑缺陷: {'; '.join(logic_errors)}"})
    total_score += logic_score

    # [Check 5: 大模型智能评价推荐零食的适配度 (30 分)]
    # 针对三名出席者，验证Agent生成的零食是否合理符合饮食禁忌
    snack_score = 0
    snack_feedback = []
    for user, diet_type in attendees.items():
        record = get_client_record(parsed_data, user)
        if record:
            snack_val = find_value_by_keywords(record, ["snack", "recommend"])
            if snack_val:
                prompt = f"Does the following snack precisely and deliciously satisfy a '{diet_type}' dietary restriction? It must be a snack name. Reply ONLY with YES or NO."
                is_valid = llm_judge_content(prompt, str(snack_val))
                if is_valid:
                    snack_score += 10
                    snack_feedback.append(f"{user}({diet_type}): 合格 ({snack_val})")
                else:
                    snack_feedback.append(f"{user}({diet_type}): 不合格 ({snack_val})")
            else:
                snack_feedback.append(f"{user}: 缺失零食信息")
        else:
             snack_feedback.append(f"{user}: 记录缺失")

    if snack_score == 30:
        details.append({"item": "利用LLM验证个性化零食推荐合理性", "score": 30, "max_score": 30, "passed": True, "reason": "推荐完美贴合饮食禁忌"})
    else:
        details.append({"item": "利用LLM验证个性化零食推荐合理性", "score": snack_score, "max_score": 30, "passed": False, "reason": f"评价明细: {'; '.join(snack_feedback)}"})
    total_score += snack_score

    return total_score, details

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    final_score, report_details = verify_workplace(workspace)
    
    report = {
        "total_score": final_score,
        "details": report_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    
    print(f"Workplace Verification Complete. Final Score: {final_score}/100")
