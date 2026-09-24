import os
import sys
import json
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 配置 LLM
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

    http_client = httpx.Client(verify=False)
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )

    def llm_judge(prompt, content):
        try:
            response = client.chat.completions.create(
                model=MOCK_MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a strict legal auditor for the Diocese. Answer ONLY 'YES' or 'NO'."},
                    {"role": "user", "content": f"{prompt}\n\n[Content]:\n{content}"}
                ],
                temperature=0
            )
            return "yes" in response.choices[0].message.content.strip().lower()
        except Exception:
            return False

    # 1. 检查交付物目录与文件是否存在 (10分)
    unauthorized_path = os.path.join(workspace, "deliverables/unauthorized_report.txt")
    audit_path = os.path.join(workspace, "deliverables/final_audit.json")
    
    dir_exists = os.path.exists(os.path.join(workspace, "deliverables"))
    if dir_exists and os.path.exists(unauthorized_path) and os.path.exists(audit_path):
        score += 10
        details.append({"item": "文件结构检查", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables 目录及所需文件均存在"})
    else:
        details.append({"item": "文件结构检查", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 deliverables 目录或必要文件"})

    # 2. 检查 unauthorized_report.txt 内容 (30分)
    if os.path.exists(unauthorized_path):
        with open(unauthorized_path, "r", encoding="utf-8") as f:
            unauthorized_content = f.read()
        
        # 必须包含 Intruder Dave 和 Evil Steve
        has_dave = "Intruder Dave" in unauthorized_content
        has_steve = "Evil Steve" in unauthorized_content
        # 不应包含合规人员
        has_mary = "Mary Sobieski" in unauthorized_content
        
        if has_dave and has_steve and not has_mary:
            score += 30
            details.append({"item": "黑名单准确性", "score": 30, "max_score": 30, "passed": True, "reason": "正确识别了非法人员且未误伤合规人员"})
        else:
            reason = f"黑名单内容有误。Dave:{has_dave}, Steve:{has_steve}, 误伤Mary:{has_mary}"
            details.append({"item": "黑名单准确性", "score": 10 if (has_dave or has_steve) else 0, "max_score": 30, "passed": False, "reason": reason})
    else:
        details.append({"item": "黑名单准确性", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})

    # 3. 检查 final_audit.json 的数值计算 (40分)
    # 计算逻辑推演:
    # Mary Sobieski: week1 (3.5) + week2 (2.5) + memo (1.0) = 7.0
    # John Kowalski: week1 (120min = 2.0) = 2.0
    # Agnieszka Novak: week2 (4.0) = 4.0
    # Robert Miller: memo (5.2) = 5.2
    # Theresa Wisniewski: memo (13:00-14:15 = 1.25 -> 1.3) = 1.3
    expected_hours = {
        "Mary Sobieski": 7.0,
        "John Kowalski": 2.0,
        "Agnieszka Novak": 4.0,
        "Robert Miller": 5.2,
        "Theresa Wisniewski": 1.3 # 75 mins
    }
    
    if os.path.exists(audit_path):
        try:
            with open(audit_path, "r", encoding="utf-8") as f:
                audit_data = json.load(f)
            
            # 兼容列表或字典格式
            if isinstance(audit_data, list):
                audit_dict = {item.get("name") or item.get("volunteer"): item.get("hours") or item.get("total_hours") for item in audit_data}
            else:
                audit_dict = audit_data

            correct_count = 0
            for name, expected in expected_hours.items():
                actual = audit_dict.get(name)
                if actual is not None and abs(float(actual) - expected) <= 0.1:
                    correct_count += 1
            
            sub_score = int((correct_count / len(expected_hours)) * 40)
            score += sub_score
            details.append({"item": "工时计算精度", "score": sub_score, "max_score": 40, "passed": correct_count == len(expected_hours), "reason": f"正确计算了 {correct_count}/{len(expected_hours)} 名志愿者的工时"})
        except Exception as e:
            details.append({"item": "工时计算精度", "score": 0, "max_score": 40, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
    else:
        details.append({"item": "工时计算精度", "score": 0, "max_score": 40, "passed": False, "reason": "文件不存在"})

    # 4. LLM 检查报告的严谨性与语气 (20分)
    if os.path.exists(unauthorized_path):
        with open(unauthorized_path, "r", encoding="utf-8") as f:
            content = f.read()
        prompt = "The report should be professional and mention that these individuals violated 'Canon Law' or failed 'Diocese Background Checks'. Does it sound like an official church audit report?"
        if llm_judge(prompt, content):
            score += 20
            details.append({"item": "报告专业性(LLM)", "score": 20, "max_score": 20, "passed": True, "reason": "报告符合教区严谨的公文格式"})
        else:
            details.append({"item": "报告专业性(LLM)", "score": 5, "max_score": 20, "passed": False, "reason": "报告语气或合规性描述不足"})
    else:
        details.append({"item": "报告专业性(LLM)", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})

    # 写入最终得分
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
