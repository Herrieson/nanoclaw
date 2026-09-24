import os
import sys
import json
import csv
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

def compute_standard_answer(workspace):
    active_vendors = {}
    sla_dir = os.path.join(workspace, "sla_contracts")
    if os.path.exists(sla_dir):
        for root, _, files in os.walk(sla_dir):
            for f in files:
                if f.endswith('.json'):
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8') as fp:
                            data = json.load(fp)
                            if data.get("status") == "active" and "vendor_name" in data and "rate_per_hour" in data:
                                active_vendors[data["vendor_name"]] = float(data["rate_per_hour"])
                    except:
                        pass

    vendor_mapping = {}
    registry_dir = os.path.join(workspace, "vendor_registry")
    if os.path.exists(registry_dir):
        for root, _, files in os.walk(registry_dir):
            for f in files:
                if f.endswith('.csv'):
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8') as fp:
                            reader = csv.DictReader(fp)
                            for row in reader:
                                if "VENDOR_CODE" in row and "ACTUAL_COMPANY_NAME" in row:
                                    vendor_mapping[row["VENDOR_CODE"]] = row["ACTUAL_COMPANY_NAME"]
                    except:
                        pass

    unauthorized_vendors = set()
    total_cost = 0.0

    timesheets_dir = os.path.join(workspace, "timesheets_dump")
    if os.path.exists(timesheets_dir):
        for root, _, files in os.walk(timesheets_dir):
            for f in files:
                if f.endswith('.csv'):
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8') as fp:
                            reader = csv.DictReader(fp)
                            for row in reader:
                                code = row.get("VendorCode")
                                if not code:
                                    continue
                                hours_str = row.get("HoursLogged", "")
                                
                                try:
                                    hours = float(hours_str)
                                    if hours <= 0:
                                        continue
                                except ValueError:
                                    continue
                                    
                                name = vendor_mapping.get(code, code)
                                if name in active_vendors:
                                    total_cost += active_vendors[name] * hours
                                else:
                                    unauthorized_vendors.add(name)
                    except:
                        pass

    return set(unauthorized_vendors), total_cost

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    # Standard computation
    std_unauthorized, std_cost = compute_standard_answer(workspace)
    
    # 1. Check deliverables file existence
    summary_path = os.path.join(workspace, "deliverables", "summary.json")
    if not os.path.exists(summary_path):
        score_details.append({"item": "Deliverable 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables/summary.json 不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return
    else:
        score_details.append({"item": "Deliverable 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10

    # 2. Schema check
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            ans_data = json.load(f)
    except Exception as e:
        score_details.append({"item": "JSON 格式解析", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return

    score_details.append({"item": "JSON 格式解析", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
    total_score += 10

    # 3. Unauthorized Vendors Check
    agent_unauthorized = ans_data.get("unauthorized_vendors")
    if not isinstance(agent_unauthorized, list):
        score_details.append({"item": "unauthorized_vendors 字段类型", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 unauthorized_vendors 列表"})
    else:
        total_score += 10
        score_details.append({"item": "unauthorized_vendors 字段类型", "score": 10, "max_score": 10, "passed": True, "reason": "字段类型正确"})
        
        agent_set = set(agent_unauthorized)
        if agent_set == std_unauthorized:
            score_details.append({"item": "未经授权的供应商名单比对", "score": 30, "max_score": 30, "passed": True, "reason": "完整且准确地识别了所有未授权供应商"})
            total_score += 30
        else:
            missing = std_unauthorized - agent_set
            extra = agent_set - std_unauthorized
            if len(missing) < 5 and len(extra) < 5:
                score_details.append({"item": "未经授权的供应商名单比对", "score": 15, "max_score": 30, "passed": False, "reason": f"部分匹配。缺少: {missing}, 多余: {extra}"})
                total_score += 15
            else:
                score_details.append({"item": "未经授权的供应商名单比对", "score": 0, "max_score": 30, "passed": False, "reason": "供应商名单严重错误或存在大量幻觉"})

    # 4. Total Authorized Cost Check
    agent_cost = ans_data.get("total_authorized_cost")
    if not isinstance(agent_cost, (int, float)):
        score_details.append({"item": "total_authorized_cost 字段类型", "score": 0, "max_score": 40, "passed": False, "reason": "未找到合法数字类型的 total_authorized_cost"})
    else:
        if abs(agent_cost - std_cost) < 0.1:
            score_details.append({"item": "合法合同总金额核算", "score": 40, "max_score": 40, "passed": True, "reason": "完美排除了所有无效工时并匹配了正确的Active费率"})
            total_score += 40
        else:
            # 可能是没排除负数等情况
            score_details.append({"item": "合法合同总金额核算", "score": 0, "max_score": 40, "passed": False, "reason": f"总金额错误，期望 {std_cost:.2f}，实际 {agent_cost:.2f}，说明处理脏数据逻辑有缺陷"})

    # Write output
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
