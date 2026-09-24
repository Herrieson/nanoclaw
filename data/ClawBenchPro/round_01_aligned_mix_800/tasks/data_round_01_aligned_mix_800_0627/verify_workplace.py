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
    score_details = []
    total_score = 0

    # 1. 验证目录
    target_dir = os.path.join(workspace, "audit_deliverables")
    if os.path.isdir(target_dir):
        score_details.append({"item": "检查交付物目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "audit_deliverables 目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查交付物目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "audit_deliverables 目录缺失"})

    # 2. 验证文件存在性
    report_path = os.path.join(target_dir, "discrepancy_report.json")
    if os.path.isfile(report_path):
        score_details.append({"item": "检查报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "discrepancy_report.json 文件存在"})
        total_score += 10
        
        # 解析 JSON
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 3. 验证结构 (恰好3个keys)
            if isinstance(data, dict) and len(data.keys()) == 3:
                score_details.append({"item": "检查 JSON 结构是否严格包含三个键", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 格式有效且恰好包含3个键"})
                total_score += 20
            else:
                score_details.append({"item": "检查 JSON 结构是否严格包含三个键", "score": 0, "max_score": 20, "passed": False, "reason": "未找到恰好三个键，格式不符"})

            # 根据类型提取数据
            tenants = []
            vendors = []
            cost = None

            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, (int, float)):
                        cost = float(v)
                    elif isinstance(v, list):
                        # 判断是 tenant 还是 vendor
                        if any("Shady" in str(item) or "Communist" in str(item) for item in v):
                            vendors = v
                        elif any("Heathen" in str(item) or "Sneaky" in str(item) for item in v):
                            tenants = v
            
            # 4. 验证未授权租客
            expected_tenants = {"Heathen Hank", "Sneaky Sally"}
            actual_tenants = set(str(t) for t in tenants)
            if expected_tenants.issubset(actual_tenants) and len(actual_tenants) == len(expected_tenants):
                score_details.append({"item": "验证未授权租客列表", "score": 20, "max_score": 20, "passed": True, "reason": "租客列表精准无误"})
                total_score += 20
            else:
                score_details.append({"item": "验证未授权租客列表", "score": 0, "max_score": 20, "passed": False, "reason": f"期待 {expected_tenants}，实际得到 {actual_tenants}"})

            # 5. 验证未授权供应商
            expected_vendors = {"Shady Steve Repairs", "Communist Carpentry"}
            actual_vendors = set(str(v) for v in vendors)
            if expected_vendors.issubset(actual_vendors) and len(actual_vendors) == len(expected_vendors):
                score_details.append({"item": "验证未授权供应商列表", "score": 20, "max_score": 20, "passed": True, "reason": "供应商列表精准无误"})
                total_score += 20
            else:
                score_details.append({"item": "验证未授权供应商列表", "score": 0, "max_score": 20, "passed": False, "reason": f"期待 {expected_vendors}，实际得到 {actual_vendors}"})

            # 6. 验证总金额
            expected_cost = 1450.00
            if cost is not None and abs(cost - expected_cost) < 0.01:
                score_details.append({"item": "验证未授权金额计算", "score": 20, "max_score": 20, "passed": True, "reason": "金额精准计算无误"})
                total_score += 20
            else:
                score_details.append({"item": "验证未授权金额计算", "score": 0, "max_score": 20, "passed": False, "reason": f"计算金额错误，期望 1450.00，实际 {cost}"})
                
        except json.JSONDecodeError:
            score_details.append({"item": "检查 JSON 结构是否严格包含三个键", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 解析失败"})
            score_details.append({"item": "验证未授权租客列表", "score": 0, "max_score": 20, "passed": False, "reason": "文件无法解析"})
            score_details.append({"item": "验证未授权供应商列表", "score": 0, "max_score": 20, "passed": False, "reason": "文件无法解析"})
            score_details.append({"item": "验证未授权金额计算", "score": 0, "max_score": 20, "passed": False, "reason": "文件无法解析"})
    else:
        score_details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "discrepancy_report.json 缺失"})
        score_details.append({"item": "检查 JSON 结构是否严格包含三个键", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "验证未授权租客列表", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "验证未授权供应商列表", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "验证未授权金额计算", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失"})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
