import os
import sys
import json
import httpx
from openai import OpenAI

# 🔒 强制 API 规范：初始化客户端并关闭 SSL 验证
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
    """统一的非结构化语义验证接口"""
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
    deliverables_path = os.path.join(workspace, "deliverables", "official_safety_report.json")
    score_details = []
    
    # 1. 检查文件是否存在与基础格式 (10分)
    if not os.path.exists(deliverables_path):
        score_details.append({"item": "文件存在性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables/official_safety_report.json"})
        total_score = 0
        final_output(total_score, score_details)
        return

    try:
        with open(deliverables_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score_details.append({"item": "JSON格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
    except Exception as e:
        score_details.append({"item": "JSON格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        final_output(0, score_details)
        return

    # 2. 检查工时计算 (20分)
    # 计算值: 14 + 20 + 8 + 22 + 16 = 80
    expected_hours = 80
    actual_hours = data.get("total_man_hours", data.get("total_hours", 0))
    if actual_hours == expected_hours:
        score_details.append({"item": "工时统计准确性", "score": 20, "max_score": 20, "passed": True, "reason": f"工时正确: {expected_hours}"})
    else:
        score_details.append({"item": "工时统计准确性", "score": 0, "max_score": 20, "passed": False, "reason": f"工时错误，期望 {expected_hours}，实际 {actual_hours}"})

    # 3. 检查违规项过滤 (40分)
    # 应包含：
    # - Scaffolding (4ft): VIOLATION (MBSC 12.4)
    # - Exposed wiring (Sector B): VIOLATION (MBSC 22.5)
    # - Hard hats (Drop zone): VIOLATION (MBSC 08.1)
    # - Trench (6ft): VIOLATION (MBSC 19.2)
    # 应排除：
    # - Easel (Driveway)
    # - Toddler/Crayon/Paint
    violations = data.get("violations", [])
    v_str = json.dumps(violations)
    
    # 细化违规项检测（代码检测关键词 + LLM检测逻辑）
    violation_score = 0
    keywords = ["scaffolding", "wiring", "hat", "trench"]
    for kw in keywords:
        if kw in v_str.lower():
            violation_score += 10
    
    score_details.append({"item": "关键违规项识别", "score": violation_score, "max_score": 40, "passed": violation_score == 40, "reason": f"识别了 {violation_score//10}/4 个核心违规点"})

    # 4. 检查是否混入个人琐事 (20分)
    prompt_noise = "Check if the report contains any non-construction personal info like 'toddler', 'painting', 'easel', 'diapers', or 'crayons'."
    has_noise = llm_judge_content(prompt_noise, v_str)
    if not has_noise:
        score_details.append({"item": "个人信息过滤", "score": 20, "max_score": 20, "passed": True, "reason": "未发现个人琐事或艺术相关干扰信息"})
    else:
        score_details.append({"item": "个人信息过滤", "score": 0, "max_score": 20, "passed": False, "reason": "报告中混入了不相关的个人生活琐事"})

    # 5. 检查是否引用了正确的法规条文 (10分)
    prompt_code = "Does the safety report correctly mention 'MBSC' or specific Section numbers (e.g., 12.4, 19.2) for the violations?"
    has_code = llm_judge_content(prompt_code, v_str)
    if has_code:
        score_details.append({"item": "法规依据合规性", "score": 10, "max_score": 10, "passed": True, "reason": "报告引用了正确的 MBSC 安全标准条文"})
    else:
        score_details.append({"item": "法规依据合规性", "score": 0, "max_score": 10, "passed": False, "reason": "未发现明确的法律法规引用（可能靠幻觉生成的违规判定）"})

    total_score = sum(d["score"] for d in score_details)
    final_output(total_score, score_details)

def final_output(total_score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": int(total_score), "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
