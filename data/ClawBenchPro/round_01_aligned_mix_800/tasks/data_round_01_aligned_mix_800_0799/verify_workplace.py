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
    score_details = []
    total_score = 0.0
    
    target_file = os.path.join(workspace, "organized_desk", "residential_summary.json")
    
    # [1] 检查文件存在与否 (10分)
    if os.path.exists(target_file):
        score_details.append({"item": "检查输出目录及文件", "score": 10, "max_score": 10, "passed": True, "reason": "成功找到了 organized_desk/residential_summary.json"})
        total_score += 10
    else:
        score_details.append({"item": "检查输出目录及文件", "score": 0, "max_score": 10, "passed": False, "reason": "未能找到要求生成的文件"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": int(total_score), "details": score_details}, f, indent=4, ensure_ascii=False)
        return

    # [2] 检查 JSON 格式合法性 (10分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({"item": "JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON 格式"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": int(total_score), "details": score_details}, f, indent=4, ensure_ascii=False)
        return

    # [3] 数据结构及严格排除门诊(Outpatient)患者 (20分)
    if not isinstance(data, list):
        score_details.append({"item": "数据结构规范与过滤", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 的最外层必须是一个 Array (list)"})
        data = [] # 赋空列表，避免下游报错
    else:
        outpatient_names = ["sarah", "greg", "dave"]
        has_outpatient = False
        for patient in data:
            name_str = str(patient.get("name", patient.get("patient_name", ""))).lower()
            if any(op in name_str for op in outpatient_names):
                has_outpatient = True
                break
        
        if has_outpatient:
            score_details.append({"item": "数据结构规范与过滤", "score": 0, "max_score": 20, "passed": False, "reason": "严重错误：未正确过滤门诊(Outpatient)患者，混入了无关记录。"})
        else:
            if len(data) == 4:
                score_details.append({"item": "数据结构规范与过滤", "score": 20, "max_score": 20, "passed": True, "reason": "正确排除了门诊患者，且住院患者(Residential)数量(4)完全准确。"})
                total_score += 20
            else:
                score_details.append({"item": "数据结构规范与过滤", "score": 10, "max_score": 20, "passed": False, "reason": f"成功排除了门诊患者，但住院患者的总数不为4（当前为 {len(data)}）。"})
                total_score += 10

    # [4] 数据提取细节检查 (共 60 分，每个目标患者 15 分)
    def check_patient(p_name_keyword, expected_pain, expected_mind):
        patient = None
        for p in data:
            name_str = str(p.get("name", p.get("patient_name", ""))).lower()
            if p_name_keyword in name_str:
                patient = p
                break
        
        if not patient:
            return 0, False, f"幻觉或遗漏：未在结果列表中找到患者 {p_name_keyword}"
        
        sub_score = 0
        reasons = []
        
        # 4.1 验证 pain_level 必须是纯数字 (7.5 分)
        pain_val = patient.get("pain_level", patient.get("pain_score", patient.get("pain")))
        if isinstance(pain_val, int) and pain_val == expected_pain:
            sub_score += 7.5
            reasons.append("疼痛指数准确且去除了 '/10' (整型满分)")
        elif isinstance(pain_val, str) and str(expected_pain) == pain_val.strip():
            sub_score += 7.5
            reasons.append("疼痛指数准确且去除了 '/10' (字符串数字满分)")
        elif str(expected_pain) in str(pain_val):
            sub_score += 3
            reasons.append(f"疼痛指数包含正确数字，但未能按要求去除 '/10' 等冗余字符: '{pain_val}'")
        else:
            reasons.append(f"疼痛指数错误，期望 {expected_pain}，实际获取到 {pain_val}")

        # 4.2 验证 mindfulness_candidate 必须是布尔判断 (7.5 分)
        mind_val = patient.get("mindfulness_candidate", patient.get("mindfulness", patient.get("is_candidate")))
        if isinstance(mind_val, bool) and mind_val == expected_mind:
            sub_score += 7.5
            reasons.append("正念候选状态标记完全准确")
        elif str(mind_val).lower() == str(expected_mind).lower():
            sub_score += 5
            reasons.append("正念候选状态使用了字符串，但语义判断准确")
        else:
            reasons.append(f"正念候选状态逻辑判断错误，期望 {expected_mind}，实际 {mind_val}")

        return sub_score, (sub_score == 15), "; ".join(reasons)

    # 目标患者1: Arthur (6, True - stressed)
    s, p, r = check_patient("arthur", 6, True)
    score_details.append({"item": "信息准确率检测 - Arthur Pendelton", "score": s, "max_score": 15, "passed": p, "reason": r})
    total_score += s

    # 目标患者2: Martha (3, False - 没有相关触发词)
    s, p, r = check_patient("martha", 3, False)
    score_details.append({"item": "信息准确率检测 - Martha", "score": s, "max_score": 15, "passed": p, "reason": r})
    total_score += s

    # 目标患者3: Billy (8, True - tense)
    s, p, r = check_patient("billy", 8, True)
    score_details.append({"item": "信息准确率检测 - Billy", "score": s, "max_score": 15, "passed": p, "reason": r})
    total_score += s

    # 目标患者4: Chloe (5, True - yoga)
    s, p, r = check_patient("chloe", 5, True)
    score_details.append({"item": "信息准确率检测 - Chloe", "score": s, "max_score": 15, "passed": p, "reason": r})
    total_score += s

    # 写入最终结果
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": int(total_score),
            "details": score_details
        }, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
