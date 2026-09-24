import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------------------------------------------------------ULN
# 配置环境与常量
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
                {"role": "system", "content": "You are a strict security audit assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

# ----------------------------------------------------------------
# 校验逻辑主体
# ----------------------------------------------------------------
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables")
    
    score_details = []
    
    # 1. 检查交付物目录与文件是否存在 (10分)
    security_alert_path = os.path.join(deliverables_path, "security_alert.txt")
    hours_report_path = os.path.join(deliverables_path, "hours_report.json")
    
    dir_exists = os.path.exists(deliverables_path)
    alert_exists = os.path.exists(security_alert_path)
    report_exists = os.path.exists(hours_report_path)
    
    score_details.append({
        "item": "Deliverables directory and files existence",
        "score": 10 if (dir_exists and alert_exists and report_exists) else 0,
        "max_score": 10,
        "passed": dir_exists and alert_exists and report_exists,
        "reason": "Files security_alert.txt and hours_report.json found." if (alert_exists and report_exists) else "Missing key files."
    })

    # 2. 检查 security_alert.txt 内容 (30分)
    # 正确的违规者应包括: "Unknown Intruder", "Bad Actor"
    if alert_exists:
        with open(security_alert_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 结构化检查：名字是否出现在文件中
        found_intruder = "Unknown Intruder" in content
        found_bad_actor = "Bad Actor" in content
        # 负向检查：合规的人不应在里面
        wrongly_flagged = "Maya Angelou" in content or "Gordon Ramsay" in content
        
        alert_score = 0
        if found_intruder: alert_score += 15
        if found_bad_actor: alert_score += 15
        if wrongly_flagged: alert_score -= 10
        
        score_details.append({
            "item": "Security Alert list accuracy",
            "score": max(0, alert_score),
            "max_score": 30,
            "passed": alert_score >= 30,
            "reason": f"Detected: Intruder={found_intruder}, Bad Actor={found_bad_actor}, False Positive={wrongly_flagged}"
        })
    else:
        score_details.append({"item": "Security Alert list accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "File missing"})

    # 3. 检查 hours_report.json 数据准确性 (40分)
    # 合规数据统计：
    # Maya Angelou: Mon(3h) + Thu(2h) = 5h
    # Gordon Ramsay: Tue(3.5h) + Thu(1h) = 4.5h
    # Alice Waters: Tue(2h) = 2h
    # Julia Child: Wed(3h) = 3h
    # Total: 14.5h
    if report_exists:
        try:
            with open(hours_report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 这里检查具体数值，必须完全解析JSON，严禁正则匹配
            maya_h = 0
            gordon_h = 0
            total_h = 0
            
            # 宽容处理 JSON 结构（可能是列表也可能是字典）
            if isinstance(data, dict):
                # 假设键是名字或有一个 details 列表
                hours_dict = data.get("volunteer_hours", data)
                maya_h = hours_dict.get("Maya Angelou", 0)
                gordon_h = hours_dict.get("Gordon Ramsay", 0)
                total_h = data.get("total_hours", 0)
            
            # 验证具体数值
            val_score = 0
            if maya_h == 5: val_score += 10
            if gordon_h == 4.5: val_score += 10
            if total_h == 14.5: val_score += 20
            
            score_details.append({
                "item": "Hours Report calculation accuracy",
                "score": val_score,
                "max_score": 40,
                "passed": val_score == 40,
                "reason": f"Maya: {maya_h}/5, Gordon: {gordon_h}/4.5, Total: {total_h}/14.5"
            })
        except Exception as e:
            score_details.append({"item": "Hours Report calculation accuracy", "score": 0, "max_score": 40, "passed": False, "reason": f"JSON parse error: {e}"})
    else:
        score_details.append({"item": "Hours Report calculation accuracy", "score": 0, "max_score": 40, "passed": False, "reason": "File missing"})

    # 4. LLM 语义检查 security_alert.txt 的警示性 (20分)
    if alert_exists:
        with open(security_alert_path, 'r', encoding='utf-8') as f:
            content = f.read()
        prompt = "Does this security alert file clearly state that unauthorized individuals were found and provide their names for emergency action?"
        llm_passed = llm_judge_content(prompt, content)
        score_details.append({
            "item": "LLM: Security Alert Tone and Clarity",
            "score": 20 if llm_passed else 0,
            "max_score": 20,
            "passed": llm_passed,
            "reason": "LLM confirmed the alert is clear and actionable." if llm_passed else "LLM found the alert vague or missing key context."
        })
    else:
        score_details.append({"item": "LLM: Security Alert Tone and Clarity", "score": 0, "max_score": 20, "passed": False, "reason": "File missing"})

    # 计算总分
    total_score = sum(item["score"] for item in score_details)
    output = {
        "total_score": int(total_score),
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
