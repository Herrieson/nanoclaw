import os
import sys
import json
import httpx
from openai import OpenAI

# 强制 API 规范
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0
    
    # Check 1: Directory and File existence (20 points)
    deliverables_dir = os.path.join(workspace, "deliverables")
    summary_path = os.path.join(deliverables_dir, "executive_summary.json")
    
    if os.path.isdir(deliverables_dir) and os.path.isfile(summary_path):
        details.append({"item": "检查交付物目录与 JSON 文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件 deliverables/executive_summary.json 存在"})
        total_score += 20
    else:
        details.append({"item": "检查交付物目录与 JSON 文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 deliverables/executive_summary.json"})
        # 严重错误，后续无从检查
        write_result(total_score, details)
        return

    # Load JSON
    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        details.append({"item": "检查 JSON 格式是否合法", "score": 0, "max_score": 80, "passed": False, "reason": "executive_summary.json 无法被解析为合法 JSON"})
        write_result(total_score, details)
        return
        
    # Check 2: Structure & Schema (10 points)
    has_unauthorized = "unauthorized_vendors" in data and isinstance(data["unauthorized_vendors"], list)
    has_total_cost = "total_authorized_expenditure" in data and isinstance(data["total_authorized_expenditure"], (int, float))
    
    if has_unauthorized and has_total_cost:
        details.append({"item": "检查 JSON Schema 字段及类型", "score": 10, "max_score": 10, "passed": True, "reason": "必需字段均存在且类型正确"})
        total_score += 10
    else:
        details.append({"item": "检查 JSON Schema 字段及类型", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 unauthorized_vendors (List) 或 total_authorized_expenditure (Number) 字段"})

    # Check 3: Unauthorized Vendors List Validation (30 points)
    # Expected: "ShadowCoders", "RogueIT Contractors"
    expected_unauth = {"shadowcoders", "rogueit contractors"}
    if has_unauthorized:
        actual_unauth = {str(v).strip().lower() for v in data["unauthorized_vendors"]}
        if actual_unauth == expected_unauth:
            details.append({"item": "核对未授权供应商名单", "score": 30, "max_score": 30, "passed": True, "reason": "未授权名单完全匹配"})
            total_score += 30
        else:
            details.append({"item": "核对未授权供应商名单", "score": 0, "max_score": 30, "passed": False, "reason": f"名单错误。期望: {expected_unauth}, 实际: {actual_unauth}"})
            
    # Check 4: Total Authorized Expenditure Calculation (40 points)
    # Expected Total:
    # CloudArchitects Inc: 20 * 180 = 3600
    # TechNova Solutions (JSON): 10 * 150 = 1500
    # TechNova Solutions (OCR): 40 * 150 = 6000
    # ByteSynergy LLC: 15 * 200 = 3000
    # Sum: 3600 + 1500 + 6000 + 3000 = 14100
    expected_cost = 14100.0
    if has_total_cost:
        actual_cost = float(data["total_authorized_expenditure"])
        if abs(actual_cost - expected_cost) < 0.01:
            details.append({"item": "核对授权供应商的总支出", "score": 40, "max_score": 40, "passed": True, "reason": f"计算精准正确: {expected_cost}"})
            total_score += 40
        else:
            # Check for partial score (e.g. missed OCR or JSON)
            if abs(actual_cost - 5100.0) < 0.01:
                details.append({"item": "核对授权供应商的总支出", "score": 10, "max_score": 40, "passed": False, "reason": "遗漏了 OCR 的数据, 计算结果为 5100.0"})
                total_score += 10
            elif abs(actual_cost - 9000.0) < 0.01:
                details.append({"item": "核对授权供应商的总支出", "score": 10, "max_score": 40, "passed": False, "reason": "遗漏了 JSON 的数据, 计算结果为 9000.0"})
                total_score += 10
            else:
                details.append({"item": "核对授权供应商的总支出", "score": 0, "max_score": 40, "passed": False, "reason": f"数值计算错误。期望: {expected_cost}, 实际: {actual_cost}"})

    write_result(total_score, details)

def write_result(total_score, details):
    res = {
        "total_score": int(total_score),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
