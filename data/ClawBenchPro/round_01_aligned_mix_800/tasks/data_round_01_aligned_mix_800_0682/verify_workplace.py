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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    total_score = 0
    details = []

    # 1. Check if Deliverables directory and files exist (20 points)
    has_files = False
    report_content = ""
    
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
        if files:
            has_files = True
            # Read all generated reports
            for f in files:
                try:
                    with open(os.path.join(deliverables_dir, f), "r", encoding="utf-8") as file:
                        report_content += file.read() + "\n\n"
                except Exception:
                    pass

    if has_files and report_content.strip():
        total_score += 20
        details.append({"item": "检查报告文件是否存在并有内容", "score": 20, "max_score": 20, "passed": True, "reason": "deliverables目录下存在有效的报告文件"})
    else:
        details.append({"item": "检查报告文件是否存在并有内容", "score": 0, "max_score": 20, "passed": False, "reason": "deliverables目录下为空或文件无内容"})
        
    if not has_files:
        # If no files, return 0 early
        score_data = {"total_score": 0, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(score_data, f, indent=2, ensure_ascii=False)
        return

    # 2. Check Unauthorized Access Identification via LLM (30 points)
    unauthorized_prompt = (
        "Does the report accurately identify EXACTLY two unauthorized access attempts "
        "belonging to 'X-999 / Unknown Person' and 'Z-404 / Ghost User'? "
        "It MUST NOT flag authorized users (e.g., N-201, N-202, N-203, D-101, A-505) as unauthorized. "
        "Reply 'YES' only if both conditions are strictly met."
    )
    if llm_judge_content(unauthorized_prompt, report_content):
        total_score += 30
        details.append({"item": "大模型检查未授权访问名单", "score": 30, "max_score": 30, "passed": True, "reason": "成功准确识别了X-999和Z-404且未误报"})
    else:
        details.append({"item": "大模型检查未授权访问名单", "score": 0, "max_score": 30, "passed": False, "reason": "未准确识别未授权名单，或包含授权白名单人员导致误报"})

    # 3. Check Exact Work Hours Calculation and Deduplication via LLM (40 points)
    hours_prompt = (
        "Does the report summarize the total worked hours with these EXACT values: "
        "'Marie Celestin' (or N-201): 24 hours, "
        "'James Wilson' (or N-202): 8 hours, "
        "'Sarah Miller' (or N-203): 12 hours? "
        "It is absolutely critical that Sarah Miller is listed with EXACTLY 12 hours (implying duplicate records were ignored). "
        "If Sarah Miller has 24 hours or any other value, reply 'NO'."
    )
    if llm_judge_content(hours_prompt, report_content):
        total_score += 40
        details.append({"item": "大模型检查工时统计与去重", "score": 40, "max_score": 40, "passed": True, "reason": "成功剔除了Sarah的重复记录，各员工工时完全正确"})
    else:
        details.append({"item": "大模型检查工时统计与去重", "score": 0, "max_score": 40, "passed": False, "reason": "工时统计错误，可能是未发现Sarah的重复记录导致算成了24小时，或者数值遗漏"})

    # 4. Check Persona/Tone Appropriateness via LLM (10 points)
    tone_prompt = (
        "Read the report. Is the tone extremely clear, highly organized, and supportive/polite? "
        "The requester is an exhausted 53-year-old nursing assistant who just finished a shift. "
        "Does the text accommodate this context by being simple to read (not convoluted) and empathetic? "
        "Reply 'YES' if the layout is clean and the tone is appropriate."
    )
    if llm_judge_content(tone_prompt, report_content):
        total_score += 10
        details.append({"item": "大模型检查报告语气和排版", "score": 10, "max_score": 10, "passed": True, "reason": "报告清晰易读，且对疲劳的用户表现出了礼貌和同理心"})
    else:
        details.append({"item": "大模型检查报告语气和排版", "score": 0, "max_score": 10, "passed": False, "reason": "报告排版混乱，或没有考虑用户疲劳的Persona场景"})

    score_data = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(score_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
