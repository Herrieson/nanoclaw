import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# 初始化客户端，强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型非结构化文本验证器"""
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

def evaluate(workspace):
    details = []
    total_score = 0
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    # 1. 检查交付物目录与文件存在性 (10分)
    has_deliverables = False
    report_content = ""
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        files = os.listdir(deliverables_dir)
        valid_files = [f for f in files if os.path.isfile(os.path.join(deliverables_dir, f))]
        if valid_files:
            has_deliverables = True
            # 读取所有报告内容合并用于后续非结构化分析
            for vf in valid_files:
                with open(os.path.join(deliverables_dir, vf), "r", encoding="utf-8") as f:
                    report_content += f.read() + "\n"
                    
    if has_deliverables:
        details.append({"item": "检查交付物目录与文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables 目录存在且包含报告文件"})
        total_score += 10
    else:
        details.append({"item": "检查交付物目录与文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录缺失或为空"})
        # 物理文件不存在直接生成 0 分报告
        return total_score, details

    # 2. 验证合法费用总和 (40分) - 精确计算值为 1050.75
    # (Travel: 345.25, Meals: 105.50, Training: 600)
    prompt_total = "Does the report explicitly state that the exact total for legitimate, approved expenses (or total excluding bird gear) is 1050.75? Look for the exact number '1050.75'."
    if llm_judge_content(prompt_total, report_content):
        details.append({"item": "验证合法费用总金额", "score": 40, "max_score": 40, "passed": True, "reason": "大模型确认报告中包含准确的合法费用总和 1050.75"})
        total_score += 40
    else:
        details.append({"item": "验证合法费用总金额", "score": 0, "max_score": 40, "passed": False, "reason": "报告中未找到准确的合法费用总和 1050.75 或计算错误"})

    # 3. 验证违规人员名单 (30分) - Bob Smith, Charlie Davis, Frank Castle
    prompt_names = "Does the report explicitly identify 'Bob Smith', 'Charlie Davis', and 'Frank Castle' as the individuals who submitted expenses for bird-watching gear? All three must be present, and NO other people should be listed as violators."
    if llm_judge_content(prompt_names, report_content):
        details.append({"item": "验证违规人员名单准确性", "score": 30, "max_score": 30, "passed": True, "reason": "大模型确认名单精准包含Bob, Charlie, Frank且无误杀"})
        total_score += 30
    else:
        details.append({"item": "验证违规人员名单准确性", "score": 0, "max_score": 30, "passed": False, "reason": "违规人员名单遗漏或包含错误人员（幻觉）"})

    # 4. 验证业务上下文与合规语气 (20分)
    prompt_context = "Does the report explicitly mention union funds, non-profit tax status, or the prohibition of bird-watching gear as context for the audit?"
    if llm_judge_content(prompt_context, report_content):
        details.append({"item": "验证审计报告上下文完整性", "score": 20, "max_score": 20, "passed": True, "reason": "报告包含了工会资金或非营利合规的业务上下文"})
        total_score += 20
    else:
        details.append({"item": "验证审计报告上下文完整性", "score": 0, "max_score": 20, "passed": False, "reason": "报告仅罗列数据，缺失题目要求的业务合规上下文"})

    return total_score, details

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score, details = evaluate(workspace)
    
    result = {
        "total_score": score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
