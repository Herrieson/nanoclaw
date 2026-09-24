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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "escalation_report")
    
    total_score = 0
    details = []

    # 1. 检查目录是否存在 (10分)
    if os.path.isdir(report_dir):
        score = 10
        total_score += score
        details.append({"item": "检查目标文件夹是否存在", "score": score, "max_score": 10, "passed": True, "reason": "escalation_report 文件夹存在"})
    else:
        details.append({"item": "检查目标文件夹是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 escalation_report 文件夹"})
        # 文件夹不存在直接短路退出
        write_result(total_score, details)
        return

    # 2. 检查是否有文件 (10分)
    files = [f for f in os.listdir(report_dir) if os.path.isfile(os.path.join(report_dir, f))]
    if files:
        score = 10
        total_score += score
        details.append({"item": "检查报告文件是否存在", "score": score, "max_score": 10, "passed": True, "reason": f"找到文件: {files}"})
    else:
        details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "escalation_report 文件夹为空"})
        write_result(total_score, details)
        return

    # 读取所有文件内容作为一个整体进行分析
    all_content = ""
    for f in files:
        try:
            with open(os.path.join(report_dir, f), 'r', encoding='utf-8', errors='ignore') as file:
                all_content += file.read() + "\n"
        except Exception:
            pass
            
    if not all_content.strip():
        details.append({"item": "检查文件内容", "score": 0, "max_score": 80, "passed": False, "reason": "文件内容为空或无法读取"})
        write_result(total_score, details)
        return

    # 核心确定性数据校验 (原生代码逻辑)
    # T-5001 (Marcus Vance)
    t5001_complaint = "The artisan carving was completely fake plastic. Furious. No one helped me."
    has_marcus = "Marcus Vance" in all_content
    has_t5001_text = t5001_complaint in all_content
    
    if has_marcus and has_t5001_text:
        score = 20
        total_score += score
        details.append({"item": "精准提取: Marcus Vance 及其投诉记录", "score": score, "max_score": 20, "passed": True, "reason": "成功提取 T-5001 的完整有效信息"})
    else:
        details.append({"item": "精准提取: Marcus Vance 及其投诉记录", "score": 0, "max_score": 20, "passed": False, "reason": "未能精准提取 Marcus Vance 或其对应的投诉原话"})

    # T-5003 (Sarah Jenkins)
    t5003_complaint = "Received a broken ceramic bowl. Customer service hung up on me."
    has_sarah = "Sarah Jenkins" in all_content
    has_t5003_text = t5003_complaint in all_content
    
    if has_sarah and has_t5003_text:
        score = 20
        total_score += score
        details.append({"item": "精准提取: Sarah Jenkins 及其投诉记录", "score": score, "max_score": 20, "passed": True, "reason": "成功提取 T-5003 的完整有效信息"})
    else:
        details.append({"item": "精准提取: Sarah Jenkins 及其投诉记录", "score": 0, "max_score": 20, "passed": False, "reason": "未能精准提取 Sarah Jenkins 或其对应的投诉原话"})

    # 严查假阳性/作弊数据 (20分)
    # 必须排除：David Kim (退款不为0), Chloe Adams (未关闭), 以及非Global Heritage的记录
    false_positives = ["David Kim", "Chloe Adams", "missing the woven basket", "damaged tapestry", "shrank after one wash", "Cable frayed"]
    found_fps = [fp for fp in false_positives if fp.lower() in all_content.lower()]
    
    if not found_fps:
        score = 20
        total_score += score
        details.append({"item": "严格过滤无效或错误数据", "score": score, "max_score": 20, "passed": True, "reason": "无幻觉，成功过滤了所有不符合条件的投诉和经理"})
    else:
        details.append({"item": "严格过滤无效或错误数据", "score": 0, "max_score": 20, "passed": False, "reason": f"存在假阳性提取，包含了错误信息: {found_fps}"})

    # LLM 语义判断：检查排版专业度和是否清晰关联经理与投诉文本 (20分)
    llm_prompt = (
        "Please evaluate the following document. "
        "Does it look like a clean, professionally compiled escalation report? "
        "It must clearly present the full names of the managers alongside their respective ignored customer complaints. "
        "It should be easy to read and suitable for a formal corporate escalation to a district director."
    )
    is_professional = llm_judge_content(llm_prompt, all_content)
    if is_professional:
        score = 20
        total_score += score
        details.append({"item": "LLM 语义验证: 专业度与清晰度", "score": score, "max_score": 20, "passed": True, "reason": "文档格式专业，清晰地将经理姓名与投诉内容关联"})
    else:
        details.append({"item": "LLM 语义验证: 专业度与清晰度", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定报告排版混乱、缺乏专业性或未清晰关联数据"})

    write_result(total_score, details)

def write_result(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Verification complete. Total Score: {total_score}")

if __name__ == "__main__":
    main()
