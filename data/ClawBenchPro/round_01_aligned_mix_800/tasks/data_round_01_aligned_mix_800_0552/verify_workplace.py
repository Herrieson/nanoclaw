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

def compute_ground_truth(workspace):
    policies_dir = os.path.join(workspace, "procurement_policies")
    syslogs_dir = os.path.join(workspace, "syslogs")
    invoices_dir = os.path.join(workspace, "data_lake", "invoices")
    
    legit_suppliers = []
    for root, _, files in os.walk(policies_dir):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "[APPROVED_BY_DIRECTOR]" in content:
                        data = json.loads(content)
                        if "active_suppliers" in data:
                            legit_suppliers = data["active_suppliers"]
            except Exception:
                pass

    received_ids = set()
    scanner_re = re.compile(r"\[SCANNER_V3\] RECV_OK:\s+(INV-\d{4}-\d{4})")
    for root, _, files in os.walk(syslogs_dir):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        match = scanner_re.search(line)
                        if match:
                            received_ids.add(match.group(1))
            except Exception:
                pass

    illegal_suppliers = set()
    total_owed_received = 0
    total_owed_pending = 0

    for root, _, files in os.walk(invoices_dir):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    inv = json.load(f)
                    if inv.get("category") in ["Lumber", "Timber"]:
                        supplier = inv.get("supplier")
                        if supplier not in legit_suppliers:
                            illegal_suppliers.add(supplier)
                        else:
                            inv_id = inv.get("invoice_id")
                            amount = inv.get("amount", 0)
                            if inv_id in received_ids:
                                total_owed_received += amount
                            else:
                                total_owed_pending += amount
            except Exception:
                pass

    return {
        "illegal_suppliers_on_invoices": sorted(list(illegal_suppliers)),
        "total_owed_received": total_owed_received,
        "total_owed_pending": total_owed_pending
    }

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "final_audit", "report.json")
    
    gt = compute_ground_truth(workspace)
    
    details = []
    total_score = 0
    
    # 1. 检查文件是否存在
    if not os.path.exists(report_path):
        details.append({"item": "检查结果文件 report.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 final_audit/report.json 文件"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f, ensure_ascii=False, indent=2)
        return
    else:
        details.append({"item": "检查结果文件 report.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功找到 report.json"})
        total_score += 10

    # 2. 检查格式
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        details.append({"item": "检查 report.json 是否为合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "检查 report.json 是否为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 3. 检查非法供应商名单 (30分)
    actual_ill_suppliers = report_data.get("illegal_suppliers_on_invoices", [])
    if not isinstance(actual_ill_suppliers, list):
        details.append({"item": "检查 illegal_suppliers_on_invoices 字段类型", "score": 0, "max_score": 10, "passed": False, "reason": "字段非数组"})
    else:
        total_score += 10
        details.append({"item": "检查 illegal_suppliers_on_invoices 字段类型", "score": 10, "max_score": 10, "passed": True, "reason": "字段为有效数组"})
        
        actual_ill_suppliers_sorted = sorted(list(set(actual_ill_suppliers)))
        if actual_ill_suppliers_sorted == gt["illegal_suppliers_on_invoices"]:
            total_score += 20
            details.append({"item": "核对非法供应商数据精准度", "score": 20, "max_score": 20, "passed": True, "reason": "筛选逻辑完全正确"})
        else:
            details.append({"item": "核对非法供应商数据精准度", "score": 0, "max_score": 20, "passed": False, "reason": f"名单错误。期望: {gt['illegal_suppliers_on_invoices']}，实际: {actual_ill_suppliers_sorted}"})

    # 4. 检查已入库欠款金额 (25分)
    actual_received = report_data.get("total_owed_received")
    if actual_received == gt["total_owed_received"]:
        total_score += 25
        details.append({"item": "核对 total_owed_received 统计结果", "score": 25, "max_score": 25, "passed": True, "reason": "已扫码入库的总欠款数额计算完全正确"})
    else:
        details.append({"item": "核对 total_owed_received 统计结果", "score": 0, "max_score": 25, "passed": False, "reason": f"金额计算错误。期望: {gt['total_owed_received']}, 实际: {actual_received}"})

    # 5. 检查未入库欠款金额 (25分)
    actual_pending = report_data.get("total_owed_pending")
    if actual_pending == gt["total_owed_pending"]:
        total_score += 25
        details.append({"item": "核对 total_owed_pending 统计结果", "score": 25, "max_score": 25, "passed": True, "reason": "未入库的货款总额计算完全正确"})
    else:
        details.append({"item": "核对 total_owed_pending 统计结果", "score": 0, "max_score": 25, "passed": False, "reason": f"金额计算错误。期望: {gt['total_owed_pending']}, 实际: {actual_pending}"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
