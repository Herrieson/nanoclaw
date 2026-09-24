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
    # 此函数为检测非结构化文本的统一接口
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

def verify_workplace(workspace_path):
    score_details = []
    total_score = 0
    
    report_path = os.path.join(workspace_path, "deliverables", "refund_report.json")
    
    # Check 1: File existence (10 pts)
    if os.path.exists(report_path):
        score_details.append({"item": "检查 deliverables/refund_report.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 deliverables/refund_report.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Check 2: Valid JSON (10 pts)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({"item": "检查 JSON 格式是否合法", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 JSON"})
        total_score += 10
    except json.JSONDecodeError:
        score_details.append({"item": "检查 JSON 格式是否合法", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 格式非法"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Check 3: Output structure correct (10 pts)
    if isinstance(data, dict) and "total" in data:
        score_details.append({"item": "检查文件结构是否为字典并包含 total 键", "score": 10, "max_score": 10, "passed": True, "reason": "结构正确"})
        total_score += 10
    else:
        score_details.append({"item": "检查文件结构是否为字典并包含 total 键", "score": 0, "max_score": 10, "passed": False, "reason": "结构错误或缺失 total 键"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Check 4: Accurate calculation for A101 (10 pts) - 5hrs + gallery = $300
    a101_val = data.get("A101")
    if a101_val == 300:
        score_details.append({"item": "账户 A101 的赔偿金计算 (300)", "score": 10, "max_score": 10, "passed": True, "reason": "计算精准"})
        total_score += 10
    else:
        score_details.append({"item": "账户 A101 的赔偿金计算 (300)", "score": 0, "max_score": 10, "passed": False, "reason": f"预期 300，实际 {a101_val}"})

    # Check 5: Accurate calculation for A102 (10 pts) - 2hrs + no keywords = $50
    a102_val = data.get("A102")
    if a102_val == 50:
        score_details.append({"item": "账户 A102 的赔偿金计算 (50)", "score": 10, "max_score": 10, "passed": True, "reason": "计算精准"})
        total_score += 10
    else:
        score_details.append({"item": "账户 A102 的赔偿金计算 (50)", "score": 0, "max_score": 10, "passed": False, "reason": f"预期 50，实际 {a102_val}"})

    # Check 6: Accurate calculation for A103 (10 pts) - 1hr + no keywords = $50
    a103_val = data.get("A103")
    if a103_val == 50:
        score_details.append({"item": "账户 A103 的赔偿金计算 (50)", "score": 10, "max_score": 10, "passed": True, "reason": "计算精准"})
        total_score += 10
    else:
        score_details.append({"item": "账户 A103 的赔偿金计算 (50)", "score": 0, "max_score": 10, "passed": False, "reason": f"预期 50，实际 {a103_val}"})

    # Check 7: Accurate calculation for A104 (10 pts) - 6hrs + sculpture = $300
    a104_val = data.get("A104")
    if a104_val == 300:
        score_details.append({"item": "账户 A104 的赔偿金计算 (300)", "score": 10, "max_score": 10, "passed": True, "reason": "计算精准"})
        total_score += 10
    else:
        score_details.append({"item": "账户 A104 的赔偿金计算 (300)", "score": 0, "max_score": 10, "passed": False, "reason": f"预期 300，实际 {a104_val}"})

    # Check 8: Accurate calculation for A106 (10 pts) - 3hrs + painting = $250
    a106_val = data.get("A106")
    if a106_val == 250:
        score_details.append({"item": "账户 A106 的赔偿金计算 (250)", "score": 10, "max_score": 10, "passed": True, "reason": "计算精准"})
        total_score += 10
    else:
        score_details.append({"item": "账户 A106 的赔偿金计算 (250)", "score": 0, "max_score": 10, "passed": False, "reason": f"预期 250，实际 {a106_val}"})

    # Check 9: Accurate handling for A105 (10 pts) - no outage = Not included or $0
    a105_val = data.get("A105", 0)
    if a105_val == 0:
        score_details.append({"item": "账户 A105 的合理排除", "score": 10, "max_score": 10, "passed": True, "reason": "由于无停电记录，正确设置金额为0或未计入"})
        total_score += 10
    else:
        score_details.append({"item": "账户 A105 的合理排除", "score": 0, "max_score": 10, "passed": False, "reason": f"A105未遭遇停电，预期应为0，实际为 {a105_val}"})

    # Check 10: Accurate Grand Total (10 pts) - 300 + 50 + 50 + 300 + 250 = 950
    total_val = data.get("total")
    if total_val == 950:
        score_details.append({"item": "总金额 total 验证 (950)", "score": 10, "max_score": 10, "passed": True, "reason": "总额计算精准"})
        total_score += 10
    else:
        score_details.append({"item": "总金额 total 验证 (950)", "score": 0, "max_score": 10, "passed": False, "reason": f"预期 950，实际 {total_val}"})

    # Write output score
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
