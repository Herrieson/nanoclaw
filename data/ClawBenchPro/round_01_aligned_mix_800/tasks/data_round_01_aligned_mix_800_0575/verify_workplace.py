import os
import sys
import json
import csv
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

def calculate_ground_truth(workspace):
    # 1. Base Inventory
    base_dir = os.path.join(workspace, "inventory/base")
    base_counts = {}
    for fname in os.listdir(base_dir):
        if fname.endswith(".json"):
            with open(os.path.join(base_dir, fname), 'r') as f:
                data = json.load(f)
                if data.get("metadata", {}).get("audit_period") == "2023-11":
                    base_counts = data.get("inventory", {})
                    break
    
    expected = base_counts.copy()
    
    # 2. Transactions
    tx_dir = os.path.join(workspace, "transactions")
    if os.path.exists(tx_dir):
        for root, _, files in os.walk(tx_dir):
            for f in files:
                if f.endswith(".jsonl"):
                    with open(os.path.join(root, f), 'r') as fin:
                        for line in fin:
                            if not line.strip(): continue
                            tx = json.loads(line)
                            if tx.get("status") == "completed":
                                d_id = tx["drug_id"]
                                qty = tx["qty"]
                                action = tx["action"]
                                if action == "dispense":
                                    expected[d_id] -= qty
                                elif action == "restock":
                                    expected[d_id] += qty

    # 3. Physical counts
    physical = {k: 0 for k in expected.keys()}
    pc_dir = os.path.join(workspace, "physical_counts")
    if os.path.exists(pc_dir):
        for f in os.listdir(pc_dir):
            if f.endswith(".csv"):
                with open(os.path.join(pc_dir, f), 'r') as fin:
                    reader = csv.DictReader(fin)
                    for row in reader:
                        d_id = row["drug_identifier"]
                        qty = int(row["counted_qty"])
                        physical[d_id] += qty
                        
    # 4. Catalog mapping
    catalog = {}
    cat_path = os.path.join(workspace, "reference/drug_catalog.csv")
    if os.path.exists(cat_path):
        with open(cat_path, 'r') as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                catalog[row["drug_id"]] = row["drug_name"]
                
    # 5. Missing calculation
    missing = {}
    for d_id, exp in expected.items():
        phys = physical.get(d_id, 0)
        if phys < exp:
            missing[catalog.get(d_id, d_id)] = exp - phys
            
    return missing

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    target_file = os.path.join(workspace, "reports/missing_drugs.json")
    
    # Check 1: File existence
    file_exists = os.path.isfile(target_file)
    if file_exists:
        results.append({"item": "检查目标结果文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件 missing_drugs.json 存在"})
        total_score += 20
    else:
        results.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 missing_drugs.json"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": results}, f, indent=2)
        return

    # Check 2: JSON Format validity
    agent_data = None
    try:
        with open(target_file, 'r') as f:
            agent_data = json.load(f)
        if isinstance(agent_data, dict):
            results.append({"item": "检查 JSON 格式与基础数据类型", "score": 10, "max_score": 10, "passed": True, "reason": "文件为合法的 JSON 字典"})
            total_score += 10
        else:
            raise ValueError("Root element is not a dict")
    except Exception as e:
        results.append({"item": "检查 JSON 格式与基础数据类型", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败或不是字典类型: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2)
        return

    # Ground Truth Calculation
    gt_missing = calculate_ground_truth(workspace)
    
    # Check 3: Drug Keys Coverage (No false positives/negatives)
    gt_keys = set(gt_missing.keys())
    agent_keys = set(agent_data.keys())
    
    missing_in_agent = gt_keys - agent_keys
    extra_in_agent = agent_keys - gt_keys
    
    key_score = 30
    reason_key = "找到的药物名单完全正确"
    if missing_in_agent or extra_in_agent:
        penalty = (len(missing_in_agent) + len(extra_in_agent)) * 2
        key_score = max(0, 30 - penalty)
        reason_key = f"存在漏报或误报 (漏报: {len(missing_in_agent)}, 误报: {len(extra_in_agent)})"
        
    results.append({"item": "比对药物名单(发现的缺失药物种类)", "score": key_score, "max_score": 30, "passed": key_score == 30, "reason": reason_key})
    total_score += key_score

    # Check 4: Exact numerical values for missing counts
    correct_values = 0
    common_keys = gt_keys.intersection(agent_keys)
    
    if len(common_keys) > 0:
        for k in common_keys:
            if agent_data[k] == gt_missing[k]:
                correct_values += 1
        
        value_score = int((correct_values / len(gt_missing)) * 40)
        passed_val = (value_score == 40)
        reason_val = f"{correct_values}/{len(gt_missing)} 个药品的数量计算完全精确"
    else:
        value_score = 0
        passed_val = False
        reason_val = "没有找到任何正确的缺失药品，无法核对数值"
        
    results.append({"item": "比对具体缺失数值", "score": value_score, "max_score": 40, "passed": passed_val, "reason": reason_val})
    total_score += value_score

    # Save metrics
    with open("workplace_score.json", "w") as f:
        json.dump({
            "total_score": total_score,
            "details": results
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
