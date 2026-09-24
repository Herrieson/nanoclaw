import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# ----------------------------------------------------------------------------
# 配置与初始化
# ----------------------------------------------------------------------------
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

# ----------------------------------------------------------------------------
# 核心验证逻辑
# ----------------------------------------------------------------------------
def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverable_path = os.path.join(workspace, "deliverables/audit_report.json")
    
    score_details = []
    total_score = 0

    # 1. 检查交付文件是否存在 (10分)
    if os.path.exists(deliverable_path):
        score_details.append({"item": "交付文件 deliverables/audit_report.json 存在", "score": 10, "max_score": 10, "passed": True})
        total_score += 10
        
        # 尝试读取并解析 JSON
        try:
            with open(deliverable_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            score_details.append({"item": "JSON 格式合法性解析", "score": 10, "max_score": 10, "passed": True})
            total_score += 10

            # 2. 检查非法人员名单 (30分)
            # 预期：John Doe, Unknown
            unauthorized = data.get("unauthorized_personnel", [])
            # 兼容大小写和列表内容
            expected_unauthorized = ["John Doe", "Unknown"]
            found_unauthorized = [name for name in expected_unauthorized if any(name.lower() in str(u).lower() for u in unauthorized)]
            
            if len(found_unauthorized) == 2:
                score_details.append({"item": "非法人员识别 (John Doe, Unknown)", "score": 30, "max_score": 30, "passed": True})
                total_score += 30
            elif len(found_unauthorized) == 1:
                score_details.append({"item": "非法人员识别 (部分缺失)", "score": 15, "max_score": 30, "passed": False, "reason": f"只找到了 {found_unauthorized}"})
                total_score += 15
            else:
                score_details.append({"item": "非法人员识别失败", "score": 0, "max_score": 30, "passed": False})

            # 3. 计算合法志愿者服务时长 (20分)
            # 预期计算过程: 
            # Sarah (45+50=95) + Michael (30+20=50) + Elena (40) + David (25) = 210
            # 注意：非法人员的时长不能计入
            actual_duration = data.get("total_authorized_duration_minutes") or data.get("total_duration")
            if str(actual_duration) == "210":
                score_details.append({"item": "合法志愿者总时长计算 (210)", "score": 20, "max_score": 20, "passed": True})
                total_score += 20
            else:
                score_details.append({"item": "合法志愿者总时长计算错误", "score": 0, "max_score": 20, "passed": False, "reason": f"预期210, 实际得到 {actual_duration}"})

            # 4. 异常血压 ID 识别 (20分)
            # 预期：104
            anomalous_ids = data.get("anomalous_bp_ids", [])
            if "104" in [str(i) for i in anomalous_ids]:
                score_details.append({"item": "异常血压 ID 识别 (104)", "score": 20, "max_score": 20, "passed": True})
                total_score += 20
            else:
                score_details.append({"item": "异常血压 ID 识别错误", "score": 0, "max_score": 20, "passed": False})

            # 5. LLM 检查报告专业性与格式 (10分)
            prompt = "The report should clearly list unauthorized staff, total duration, and anomalous IDs. Is the report professionally structured and accurate based on medical audit standards?"
            if llm_judge_content(prompt, json.dumps(data)):
                score_details.append({"item": "LLM 审计报告专业度评价", "score": 10, "max_score": 10, "passed": True})
                total_score += 10
            else:
                score_details.append({"item": "LLM 审计报告专业度评价", "score": 0, "max_score": 10, "passed": False, "reason": "报告内容不完整或表达不专业"})

        except Exception as e:
            score_details.append({"item": "JSON 解析失败或内容结构错误", "score": 0, "max_score": 80, "passed": False, "reason": str(e)})

    else:
        score_details.append({"item": "交付文件不存在", "score": 0, "max_score": 100, "passed": False})

    # 输出结果
    result = {
        "total_score": int(total_score),
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
