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
    # 此函数为检测非结构化文本的统一接口
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
    board_dir = os.path.join(workspace, "board_submission")
    
    score = 0
    details = []
    
    # 1. 检查目标目录是否存在 (5分)
    if os.path.isdir(board_dir):
        score += 5
        details.append({"item": "检查目录 board_submission 是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录已创建"})
    else:
        details.append({"item": "检查目录 board_submission 是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "目标目录不存在"})
        
    # 2. 检查志愿时长 JSON 文件格式合法性 (10分)
    json_path = os.path.join(board_dir, "verified_hours.json")
    json_data = None
    if os.path.isfile(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            score += 10
            details.append({"item": "检查 JSON 文件是否存在且格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且能被合法解析"})
        except Exception as e:
            details.append({"item": "检查 JSON 文件是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析JSON失败，存在语法错误或非标准JSON: {e}"})
    else:
        details.append({"item": "检查 JSON 文件是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件 verified_hours.json 缺失"})
        
    # 3. 检查数据过滤严谨性（无幻觉、剔除违规名单） (15分)
    if json_data is not None and isinstance(json_data, dict):
        approved_staff = {"Dr. Adams", "Nurse Sarah", "Dr. Chen", "Paramedic Joe"}
        actual_keys = set(json_data.keys())
        
        if len(actual_keys) > 0 and actual_keys.issubset(approved_staff):
            score += 15
            details.append({"item": "检查是否精确过滤并剔除了未批准员工", "score": 15, "max_score": 15, "passed": True, "reason": "无多余字段，仅包含在合规名单内的员工"})
        else:
            violation = actual_keys - approved_staff
            details.append({"item": "检查是否精确过滤并剔除了未批准员工", "score": 0, "max_score": 15, "passed": False, "reason": f"数据不严谨，包含了未批准人员或大模型幻觉的键值: {violation}"})
            
        # 4. 细粒度数据计算验证：检查数值累加是否绝对正确 (40分, 每个通过的员工得10分)
        expected_hours = {
            "Dr. Adams": 16,     # 12 (csv) + 4 (log) = 16
            "Nurse Sarah": 13,   # 8 (csv) + 5 (txt) = 13
            "Dr. Chen": 10,      # 10 (txt) = 10
            "Paramedic Joe": 15  # 15 (log) = 15
        }
        
        calc_score = 0
        calc_reasons = []
        for staff, exp_val in expected_hours.items():
            actual_val = json_data.get(staff)
            # 兼容可能的数值型或字符串型整数
            if actual_val in (exp_val, str(exp_val), float(exp_val)):
                calc_score += 10
                calc_reasons.append(f"{staff}:正确")
            else:
                calc_reasons.append(f"{staff}:错误(应得{exp_val}, 实得{actual_val})")
                
        score += calc_score
        details.append({"item": "验证各合法员工的累加工作时数准确性", "score": calc_score, "max_score": 40, "passed": calc_score == 40, "reason": "; ".join(calc_reasons)})
    else:
        details.append({"item": "检查是否精确过滤并剔除了未批准员工", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 文件不是一个键值对对象，无法验证"})
        details.append({"item": "验证各合法员工的累加工作时数准确性", "score": 0, "max_score": 40, "passed": False, "reason": "JSON 文件不是一个键值对对象，无法计算"})

    # 5. 检查病人联系信息文件存在性 (10分)
    contact_path = os.path.join(board_dir, "luthier_contact.txt")
    if os.path.isfile(contact_path):
        score += 10
        details.append({"item": "检查联系人文本 luthier_contact.txt 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建"})
        
        # 6. 利用 LLM 验证非结构化文本内的意图及关键电话号码 (20分)
        with open(contact_path, "r", encoding="utf-8") as f:
            contact_content = f.read()
        prompt = "Determine if the following text accurately isolates and provides the phone number '555-0199-OUD' for the luthier patient. Respond 'YES' if the number is present and the context matches a contact detail note, otherwise 'NO'. Do not accept arbitrary strings without the specific number."
        if llm_judge_content(prompt, contact_content):
            score += 20
            details.append({"item": "利用大模型检查提取出的联系电话是否正确有效", "score": 20, "max_score": 20, "passed": True, "reason": "大模型确认文件中包含且成功提取出该患者的准确电话号码"})
        else:
            details.append({"item": "利用大模型检查提取出的联系电话是否正确有效", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定文件中未正确提取电话号码 555-0199-OUD 或伴杂无关/错误的推测内容"})
    else:
        details.append({"item": "检查联系人文本 luthier_contact.txt 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "联系人文件不存在"})
        details.append({"item": "利用大模型检查提取出的联系电话是否正确有效", "score": 0, "max_score": 20, "passed": False, "reason": "因联系人文件缺失无法检测内容"})

    # 统一写入 workplace_score.json
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
