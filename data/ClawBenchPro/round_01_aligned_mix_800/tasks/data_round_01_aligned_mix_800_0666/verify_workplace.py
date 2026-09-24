import os
import sys
import json
import httpx
import re
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
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

def verify(workspace_dir):
    deliverables_dir = os.path.join(workspace_dir, "deliverables")
    
    score_details = []
    total_score = 0
    
    # Check 1: Directory and File Existence (10 points)
    has_file = False
    target_content = ""
    target_filename = ""
    
    if os.path.isdir(deliverables_dir):
        files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
        if files:
            has_file = True
            target_filename = files[0]
            try:
                with open(os.path.join(deliverables_dir, target_filename), "r", encoding="utf-8") as f:
                    target_content = f.read()
            except Exception:
                pass

    if has_file and target_content:
        score_details.append({"item": "检查交付物目录与文件", "score": 10, "max_score": 10, "passed": True, "reason": f"成功在 deliverables 下找到并读取报告文件: {target_filename}"})
        total_score += 10
    else:
        score_details.append({"item": "检查交付物目录与文件", "score": 0, "max_score": 10, "passed": False, "reason": "未在 deliverables 目录下找到可读的报告文件"})
        # 核心文件缺失，直接返回 0 分并终止后续验证
        with open(os.path.join(workspace_dir, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2)
        return

    # Check 2: Exact Math for Sustainable Expenses (30 points)
    # 严格使用正则提取准确的数字结果，禁止使用大模型去验证具体数值。
    # 正确的答案应该是 1200.00 + 150.50 + 45.25 = 1395.75
    # 允许的格式包含 1395.75, 1,395.75 等
    amount_pattern = r'1[,\s]*395\.75'
    if re.search(amount_pattern, target_content):
        score_details.append({"item": "精准提取可持续支出总额", "score": 30, "max_score": 30, "passed": True, "reason": "成功在报告中匹配到精确的总支出金额 1395.75"})
        total_score += 30
    else:
        score_details.append({"item": "精准提取可持续支出总额", "score": 0, "max_score": 30, "passed": False, "reason": "报告中未包含精确计算的可持续支出总额 1395.75，计算逻辑错误或格式未体现完整数值"})

    # Check 3: LLM verifies valid attendees (30 points)
    # Alice Smith, Charlie Brown, Evan Wright should be explicitly in the cleared list.
    prompt_valid = (
        "Does the following report explicitly state that 'Alice Smith', 'Charlie Brown', and 'Evan Wright' "
        "are the cleared/approved attendees? (All three must be present in the final positive list to answer YES)"
    )
    is_valid_present = llm_judge_content(prompt_valid, target_content)
    if is_valid_present:
        score_details.append({"item": "LLM 语义校验合法参会者", "score": 30, "max_score": 30, "passed": True, "reason": "所有合法且签署同意书的参会者均被正确列出"})
        total_score += 30
    else:
        score_details.append({"item": "LLM 语义校验合法参会者", "score": 0, "max_score": 30, "passed": False, "reason": "缺失合法参会者，或未将其明确作为最终名单列出"})

    # Check 4: LLM verifies exclusion of invalid attendees (30 points)
    # Bob Jones (no consent), Diana Prince (pending), Frank Ocean (did not attend) MUST NOT be in the cleared list.
    prompt_invalid = (
        "Does the following report completely EXCLUDE 'Bob Jones', 'Diana Prince', and 'Frank Ocean' "
        "from the list of cleared/approved attendees? "
        "If ANY of them are presented as cleared/approved, answer NO. If they are correctly omitted or explicitly marked as rejected/not cleared, answer YES."
    )
    is_invalid_excluded = llm_judge_content(prompt_invalid, target_content)
    if is_invalid_excluded:
        score_details.append({"item": "LLM 语义校验非法参会者剔除", "score": 30, "max_score": 30, "passed": True, "reason": "未签署、挂起或未出席的人员被正确排除出了最终白名单"})
        total_score += 30
    else:
        score_details.append({"item": "LLM 语义校验非法参会者剔除", "score": 0, "max_score": 30, "passed": False, "reason": "不符合条件的参会者错误地混入了通过名单中"})

    # Output final JSON
    with open(os.path.join(workspace_dir, "workplace_score.json"), "w") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
