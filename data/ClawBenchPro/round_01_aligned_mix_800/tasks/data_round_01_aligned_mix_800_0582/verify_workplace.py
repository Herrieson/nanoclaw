import os
import sys
import json
import re
import httpx
from openai import OpenAI

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

def verify_workplace(workspace):
    report_dir = os.path.join(workspace, "manager_report")
    
    total_score = 0
    details = []

    # 1. 检查目录 (10分)
    if os.path.isdir(report_dir):
        total_score += 10
        details.append({"item": "检查 manager_report 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        details.append({"item": "检查 manager_report 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        # 目录不存在直接结算
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. 检查是否有文件 (10分)
    files = [f for f in os.listdir(report_dir) if os.path.isfile(os.path.join(report_dir, f))]
    if files:
        total_score += 10
        details.append({"item": "检查报告文件是否生成", "score": 10, "max_score": 10, "passed": True, "reason": f"找到文件: {files[0]}"})
    else:
        details.append({"item": "检查报告文件是否生成", "score": 0, "max_score": 10, "passed": False, "reason": "目录为空"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 读取第一个文件的内容
    report_file = os.path.join(report_dir, files[0])
    try:
        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        details.append({"item": "读取报告文件", "score": 0, "max_score": 0, "passed": False, "reason": f"无法读取文件: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. LLM 检查危险名单人员 Frank Wolf (10分)
    p1 = "Does the text explicitly state that 'Frank Wolf' is in the Danger List (or has >10 hours but is NOT certified)?"
    if llm_judge_content(p1, content):
        total_score += 10
        details.append({"item": "危险名单包含 Frank Wolf", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定包含正确人员"})
    else:
        details.append({"item": "危险名单包含 Frank Wolf", "score": 0, "max_score": 10, "passed": False, "reason": "遗漏 Frank Wolf"})

    # 4. LLM 检查危险名单人员 Ghost User (10分)
    p2 = "Does the text explicitly state that 'Ghost User' is in the Danger List (or has >10 hours but is NOT certified)?"
    if llm_judge_content(p2, content):
        total_score += 10
        details.append({"item": "危险名单包含 Ghost User", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定包含正确人员"})
    else:
        details.append({"item": "危险名单包含 Ghost User", "score": 0, "max_score": 10, "passed": False, "reason": "遗漏 Ghost User"})

    # 5. LLM 检查危险名单人员 Eve Adams (10分)
    p3 = "Does the text explicitly state that 'Eve Adams' is in the Danger List (or has >10 hours but is NOT certified)?"
    if llm_judge_content(p3, content):
        total_score += 10
        details.append({"item": "危险名单包含 Eve Adams", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定包含正确人员"})
    else:
        details.append({"item": "危险名单包含 Eve Adams", "score": 0, "max_score": 10, "passed": False, "reason": "遗漏 Eve Adams"})

    # 6. 严查幻觉与作弊 (20分)
    p4 = "Does the text mistakenly include 'Old Man Jenkins', 'Alice Black', or 'Charlie Green' in the Danger List? Answer YES if any of them are wrongly included in the danger/uncertified list, otherwise NO."
    # 期望回答 NO
    if not llm_judge_content(p4, content):
        total_score += 20
        details.append({"item": "排除非危险人员与旧数据干扰", "score": 20, "max_score": 20, "passed": True, "reason": "未包含错误人员"})
    else:
        details.append({"item": "排除非危险人员与旧数据干扰", "score": 0, "max_score": 20, "passed": False, "reason": "包含了不应出现的已认证人员或旧年份人员"})

    # 7. 资金总额精准匹配与语义双重校验 (30分)
    # 原生代码验证确定性数字
    has_exact_number = bool(re.search(r'475\.75', content))
    if not has_exact_number:
        details.append({"item": "计算资金总额", "score": 0, "max_score": 30, "passed": False, "reason": "代码未能从文件中提取出精准数字 475.75"})
    else:
        # 数字存在，利用大模型验证语义关联
        p5 = "Does the text explicitly link the number '475.75' to the total certified funding, total donations of certified personnel, or similar concept?"
        if llm_judge_content(p5, content):
            total_score += 30
            details.append({"item": "计算资金总额", "score": 30, "max_score": 30, "passed": True, "reason": "数字准确且语义关联正确"})
        else:
            details.append({"item": "计算资金总额", "score": 0, "max_score": 30, "passed": False, "reason": "包含475.75，但未正确描述其为认证人员资金总额"})

    # 输出结果
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(ws)
