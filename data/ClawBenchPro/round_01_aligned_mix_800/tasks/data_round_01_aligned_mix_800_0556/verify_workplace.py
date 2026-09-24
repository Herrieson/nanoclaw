import os
import sys
import json
import httpx
from openai import OpenAI

# 强制环境变量与 API 规范
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_extract_structured_data(file_content):
    """使用 LLM 从非结构化文本中安全地提取核心指标，供后续纯代码验证"""
    prompt = """
    You are a data extraction assistant. Read the provided text and extract the following information into a strict JSON format.
    1. "total_pay": The total expected pay for October (a float number, e.g., 377.00). If not found, use null.
    2. "conflict_dates": A list of dates mentioned as problematic/conflicting Thursdays, in "YYYY-MM-DD" format. If none, use [].
    
    Output ONLY valid JSON, no markdown, no explanation.
    Example: {"total_pay": 100.50, "conflict_dates": ["2023-10-01"]}
    """
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": file_content}
            ],
            temperature=0
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"LLM Extraction Error: {e}")
        return {"total_pay": None, "conflict_dates": []}

def llm_judge_empathy(file_content):
    """调用大模型检查 Agent 的回信是否对 Elena 表达了适当的礼貌或安慰（语义层面）"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict conversational auditor. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"Does the following message sound helpful, polite, and address the context of Elena's busy life and children?\n\n[Message]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_dir = os.path.join(workspace, "family_planning")
    
    total_score = 0
    details = []

    # Check 1: 目录和文件存在性 (10 points)
    if not os.path.exists(target_dir):
        details.append({"item": "检查目标目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "family_planning 目录不存在"})
        return write_score(total_score, details)
    
    files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
    if not files:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "family_planning 目录下没有任何文件"})
        return write_score(total_score, details)
    
    details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"成功找到文件: {files[0]}"})
    
    # Read content
    file_path = os.path.join(target_dir, files[0])
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract structured data
    extracted_data = llm_extract_structured_data(content)
    pay = extracted_data.get("total_pay")
    dates = extracted_data.get("conflict_dates", [])

    # Check 2: 薪资计算精确度 (35 points) - 严格代码判定
    if pay is not None and abs(float(pay) - 377.00) < 0.01:
        details.append({"item": "验证 10 月总薪水金额", "score": 35, "max_score": 35, "passed": True, "reason": "精确匹配正确金额: $377.00"})
        total_score += 35
    else:
        details.append({"item": "验证 10 月总薪水金额", "score": 0, "max_score": 35, "passed": False, "reason": f"金额计算错误或未找到，期望 377.00，提取到: {pay}"})

    # Check 3: 冲突日期精准命中 (35 points) - 严格代码判定
    expected_dates = {"2023-10-05", "2023-10-19"}
    found_dates = set(dates)
    
    if expected_dates.issubset(found_dates):
        details.append({"item": "验证是否找到所有冲突日期", "score": 35, "max_score": 35, "passed": True, "reason": "正确指出了 10-05 和 10-19 两个冲突日期"})
        total_score += 35
    else:
        missing = expected_dates - found_dates
        details.append({"item": "验证是否找到所有冲突日期", "score": 0, "max_score": 35, "passed": False, "reason": f"遗漏了冲突日期: {missing}"})

    # Check 4: 无幻觉/误报惩罚检测 (10 points) - 严格代码判定
    unexpected_dates = found_dates - expected_dates
    if unexpected_dates:
        details.append({"item": "严查幻觉与错误时间（假阳性）", "score": 0, "max_score": 10, "passed": False, "reason": f"报告了错误的冲突日期（幻觉/边界计算错误）: {unexpected_dates}"})
    elif expected_dates.issubset(found_dates): # Only give points if it actually found the right ones AND no extras
        details.append({"item": "严查幻觉与错误时间（假阳性）", "score": 10, "max_score": 10, "passed": True, "reason": "没有误报任何不存在冲突或非10月份的日期"})
        total_score += 10
    else:
        details.append({"item": "严查幻觉与错误时间（假阳性）", "score": 0, "max_score": 10, "passed": False, "reason": "由于未能找全正确日期，本项不给分"})

    # Check 5: 语义/语气验证 (10 points) - LLM 判定
    is_empathetic = llm_judge_empathy(content)
    if is_empathetic:
        details.append({"item": "邮件语气与人文关怀", "score": 10, "max_score": 10, "passed": True, "reason": "回信语气得体，符合帮 Elena 解决麻烦的情境"})
        total_score += 10
    else:
        details.append({"item": "邮件语气与人文关怀", "score": 0, "max_score": 10, "passed": False, "reason": "未针对 Elena 的困境表达关怀或语气生硬"})

    write_score(total_score, details)

def write_score(total, details):
    res = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    verify()
