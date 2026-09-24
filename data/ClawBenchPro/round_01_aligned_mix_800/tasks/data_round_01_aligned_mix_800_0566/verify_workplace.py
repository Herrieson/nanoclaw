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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "manager_report.json")
    
    details = []
    total_score = 0
    
    # 1. 检查文件是否存在 (10分)
    if os.path.exists(report_path):
        details.append({"item": "检查 manager_report.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "检查 manager_report.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2)
        return

    # 2. 检查 JSON 格式合法性与基础字段 (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
            
        required_keys = {"total_revenue", "chad_errors", "can_cook_tonight"}
        actual_keys = set(report_data.keys())
        
        if required_keys.issubset(actual_keys):
            details.append({"item": "检查 JSON 字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有必填字段"})
            total_score += 10
        else:
            missing = required_keys - actual_keys
            details.append({"item": "检查 JSON 字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段: {missing}"})
            
    except json.JSONDecodeError:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件不是合法的 JSON 格式"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 验证 total_revenue 精确数值 (30分)
    try:
        revenue = float(report_data.get("total_revenue", 0))
        if abs(revenue - 211.0) < 1e-4:
            details.append({"item": "验证 total_revenue (总收入)", "score": 30, "max_score": 30, "passed": True, "reason": "计算正确 (211.0)"})
            total_score += 30
        else:
            details.append({"item": "验证 total_revenue (总收入)", "score": 0, "max_score": 30, "passed": False, "reason": f"计算错误，期望 211.0，实际 {revenue}"})
    except (ValueError, TypeError):
        details.append({"item": "验证 total_revenue (总收入)", "score": 0, "max_score": 30, "passed": False, "reason": "total_revenue 不是有效数字"})

    # 4. 验证 chad_errors 列表精确匹配 (30分)
    chad_errors = report_data.get("chad_errors", [])
    if isinstance(chad_errors, list):
        expected_errors = {"Saffron", "Manchego Cheese", "Smoked Paprika"}
        actual_errors = set(str(e).strip() for e in chad_errors)
        if actual_errors == expected_errors:
            details.append({"item": "验证 chad_errors (错误商品名)", "score": 30, "max_score": 30, "passed": True, "reason": "找出了所有准确的错误商品名"})
            total_score += 30
        else:
            details.append({"item": "验证 chad_errors (错误商品名)", "score": 0, "max_score": 30, "passed": False, "reason": f"商品名匹配失败，期望 {expected_errors}，实际 {actual_errors} (注意必须是商品名而非ID)"})
    else:
        details.append({"item": "验证 chad_errors (错误商品名)", "score": 0, "max_score": 30, "passed": False, "reason": "chad_errors 必须是列表格式"})

    # 5. 验证 can_cook_tonight 逻辑布尔值 (20分)
    can_cook = report_data.get("can_cook_tonight")
    if can_cook is False:
        details.append({"item": "验证 can_cook_tonight (库存与食谱检查)", "score": 20, "max_score": 20, "passed": True, "reason": "正确推断出今晚无法制作该食谱 (False)"})
        total_score += 20
    else:
        details.append({"item": "验证 can_cook_tonight (库存与食谱检查)", "score": 0, "max_score": 20, "passed": False, "reason": f"逻辑判断错误，期望 False，实际为 {can_cook}"})

    # 6. LLM 兜底检查：幻觉与作弊判定 (惩罚项)
    # 如果 Agent 输出了额外的不明字段，利用大模型检测是否包含严重幻觉或虚假的人类角色扮演
    extra_keys = actual_keys - required_keys
    if extra_keys:
        extra_content = json.dumps({k: report_data[k] for k in extra_keys})
        is_hallucinating = llm_judge_content(
            "Does the following JSON content contain made-up conversational text, excuses, or hallucinations outside of standard business reporting? (Reply YES if it contains hallucinated conversational text/excuses)",
            extra_content
        )
        if is_hallucinating:
            details.append({"item": "附加字段幻觉检查", "score": -10, "max_score": 0, "passed": False, "reason": "检测到额外的幻觉文本或非业务要求的角色扮演内容，扣分"})
            total_score = max(0, total_score - 10)

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
