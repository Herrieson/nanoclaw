import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证，满足隔离环境下的评测需求
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型作为法官，针对非结构化文本进行语义与幻觉检测"""
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
    score = 0
    details = []

    deliverables_dir = os.path.join(workspace, "deliverables")
    
    # [1] 结构与确定性解析：物理目录检查 (20分)
    if os.path.isdir(deliverables_dir):
        score += 20
        details.append({"item": "交付目录检查", "score": 20, "max_score": 20, "passed": True, "reason": "成功创建并定位到 deliverables 目录"})
    else:
        details.append({"item": "交付目录检查", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 deliverables 目录，任务严重失败"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # [2] 结构与确定性解析：产物文件检查 (20分)
    files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
    if not files:
        details.append({"item": "总结报告文件检查", "score": 0, "max_score": 20, "passed": False, "reason": "deliverables 目录为空，未生成任何报告文件"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)
        return
    else:
        score += 20
        details.append({"item": "总结报告文件检查", "score": 20, "max_score": 20, "passed": True, "reason": f"在 deliverables 中找到产出文件: {files}"})

    # 读取所有生成文本的内容，交由 LLM 进行语义级校验
    content = ""
    for file_name in files:
        file_path = os.path.join(deliverables_dir, file_name)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content += f"\n--- Content of {file_name} ---\n{f.read()}\n"
        except Exception:
            pass

    # [3] LLM 语义与精确数值校验：计算特定志愿活动的时长 (30分)
    # 计算逻辑推导: Park Cleanup (12.5 + 15.0 + 20.5) = 48.0 
    prompt_hours = (
        "Check if the report explicitly states that the total volunteer hours for 'Park Cleanup' is exactly 48 or 48.0. "
        "The number 48 must be clearly and solely associated with 'Park Cleanup'. "
        "If they mixed it up with 'Food Drive' or 'Voter Reg', or got the math wrong, answer NO. "
        "Answer YES only if the exact 48 hours is correctly extracted and summarized for Park Cleanup."
    )
    if llm_judge_content(prompt_hours, content):
        score += 30
        details.append({"item": "志愿活动时长精准提炼", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定：成功从 OCR 数据中过滤杂项并精确计算出 Park Cleanup 的总时长 (48小时)"})
    else:
        details.append({"item": "志愿活动时长精准提炼", "score": 0, "max_score": 30, "passed": False, "reason": "大模型判定：时长计算错误或混淆了其他无关志愿活动，未能精准得出 48 小时"})

    # [4] LLM 语义校验：识别挂起 (Pending/Flaky) 的企业名单 (30分)
    prompt_businesses = (
        "Check if the report explicitly mentions specific corporate sponsor names and identifies them as 'Pending', 'flaky', or having payment issues. "
        "Answer YES if at least one business name is listed along with a clear indication of a pending/manual check status. Answer NO if no business names are flagged."
    )
    if llm_judge_content(prompt_businesses, content):
        score += 30
        details.append({"item": "Pending 企业名单汇总", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定：报告成功列出并指控了处于 Pending 状态的企业赞助商"})
    else:
        details.append({"item": "Pending 企业名单汇总", "score": 0, "max_score": 30, "passed": False, "reason": "大模型判定：未能识别出 Pending 状态的企业名单"})

    # 输出规范化计分结果
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
