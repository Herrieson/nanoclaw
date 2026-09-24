import os
import sys
import json
import csv
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

def calculate_ground_truth(workspace):
    """
    Since the environment builder includes random noise which affects BOTH
    the overcharge calculations (e.g. noise might generate CleanCorp selling GEAR_44 at 10.00)
    and the total stock levels, we MUST dynamically recalculate the ground truth 
    from the generated files to prevent false negatives.
    """
    contracts = {}
    contract_path = os.path.join(workspace, "contracts", "master_contract.json")
    if not os.path.exists(contract_path):
        return 0.0, set()
    
    with open(contract_path, "r") as f:
        for item in json.load(f):
            contracts[item['id']] = item['price']
            
    total_overcharge = 0.0
    stock = {k: 0 for k in contracts.keys()}
    
    # 1. Parse CSV (active_log_alpha.csv)
    try:
        csv_path = os.path.join(workspace, "archives/storage_west/logs/active_log_alpha.csv")
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item_id = row['item_id']
                qty = int(row['qty'])
                rate = float(row['rate'])
                vendor = row['vendor']
                if item_id in stock:
                    stock[item_id] += qty
                if vendor == "CleanCorp" and item_id in contracts and rate > contracts[item_id]:
                    total_overcharge += (rate - contracts[item_id]) * qty
    except Exception:
        pass
        
    # 2. Parse JSON (active_log_beta.json)
    try:
        json_path = os.path.join(workspace, "archives/vault/backups/active_log_beta.json")
        with open(json_path, "r") as f:
            data = json.load(f)
            for row in data:
                item_id = row['item_id']
                qty = int(row['amount'])
                rate = float(row['unit_cost'])
                vendor = row['provider']
                if item_id in stock:
                    stock[item_id] += qty
                if vendor == "CleanCorp" and item_id in contracts and rate > contracts[item_id]:
                    total_overcharge += (rate - contracts[item_id]) * qty
    except Exception:
        pass

    # 3. Parse TXT (active_fragment_gamma.txt)
    try:
        txt_path = os.path.join(workspace, "archives/storage_east/temp/active_fragment_gamma.txt")
        with open(txt_path, "r") as f:
            for line in f:
                if line.startswith("ENTRY|"):
                    parts = line.strip().split("|")
                    row_data = {}
                    for p in parts[1:]:
                        if ":" in p:
                            k, v = p.split(":", 1)
                            row_data[k] = v
                    item_id = row_data.get('ITEM')
                    qty = int(row_data.get('QTY', 0))
                    rate = float(row_data.get('PRICE', 0.0))
                    vendor = row_data.get('SUPPLIER')
                    if item_id in stock:
                        stock[item_id] += qty
                    if vendor == "CleanCorp" and item_id in contracts and rate > contracts[item_id]:
                        total_overcharge += (rate - contracts[item_id]) * qty
    except Exception:
        pass
        
    low_stock_items = {k for k, v in stock.items() if v < 15}
    return total_overcharge, low_stock_items

def extract_amount(text):
    # Extracts the last prominent float number in the text
    matches = re.findall(r'\b\d+\.\d{2}\b', text)
    if matches:
        return float(matches[-1])
    return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    
    # Calculate truth
    gt_overcharge, gt_low_stock = calculate_ground_truth(workspace)
    
    reports_dir = os.path.join(workspace, "reports")
    discrepancy_file = os.path.join(reports_dir, "Discrepancy_Report.txt")
    restock_file = os.path.join(reports_dir, "Restock_Order.json")
    
    # 1. Directory and Basic files check (15 pts)
    if os.path.isdir(reports_dir):
        details.append({"item": "reports directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Directory verified."})
        total_score += 5
    else:
        details.append({"item": "reports directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "reports/ directory missing."})
        
    if os.path.isfile(discrepancy_file):
        details.append({"item": "Discrepancy_Report.txt exists", "score": 5, "max_score": 5, "passed": True, "reason": "File exists."})
        total_score += 5
    else:
        details.append({"item": "Discrepancy_Report.txt exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing report file."})

    has_valid_json = False
    restock_data = None
    if os.path.isfile(restock_file):
        try:
            with open(restock_file, "r") as f:
                restock_data = json.load(f)
            details.append({"item": "Restock_Order.json is valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "Valid JSON format."})
            total_score += 5
            has_valid_json = True
        except json.JSONDecodeError:
            details.append({"item": "Restock_Order.json is valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": "JSON decode error."})
    else:
        details.append({"item": "Restock_Order.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing restock file."})

    # 2. Precision check for Total Amount (35 pts)
    txt_content = ""
    if os.path.isfile(discrepancy_file):
        with open(discrepancy_file, "r") as f:
            txt_content = f.read()
        extracted_amount = extract_amount(txt_content)
        
        if extracted_amount is not None:
            if abs(extracted_amount - gt_overcharge) < 0.01:
                details.append({"item": "Overcharge calculation accuracy", "score": 35, "max_score": 35, "passed": True, "reason": f"Agent correctly identified total overcharge: {gt_overcharge:.2f}."})
                total_score += 35
            else:
                details.append({"item": "Overcharge calculation accuracy", "score": 0, "max_score": 35, "passed": False, "reason": f"Calculated value {extracted_amount} does not match Ground Truth {gt_overcharge:.2f}. Agent likely failed to aggregate all active files or filter out noise."})
        else:
            details.append({"item": "Overcharge calculation accuracy", "score": 0, "max_score": 35, "passed": False, "reason": "Could not extract a valid number with 2 decimal places from the text."})
    else:
        details.append({"item": "Overcharge calculation accuracy", "score": 0, "max_score": 35, "passed": False, "reason": "File missing."})

    # 3. Precision check for Low Stock Aggregation (40 pts)
    if has_valid_json:
        # Normalize agent's parsed list
        if isinstance(restock_data, list):
            agent_items = set(str(i) for i in restock_data)
        elif isinstance(restock_data, dict):
            # Fallback if agent provided dict { "items": [...] }
            # find first list inside
            agent_items = set()
            for v in restock_data.values():
                if isinstance(v, list):
                    agent_items = set(str(i) for i in v)
                    break
        else:
            agent_items = set()
            
        if agent_items == gt_low_stock:
            details.append({"item": "Low stock items accuracy", "score": 40, "max_score": 40, "passed": True, "reason": "Agent aggregated stock levels correctly across all fragments."})
            total_score += 40
        else:
            details.append({"item": "Low stock items accuracy", "score": 0, "max_score": 40, "passed": False, "reason": f"Agent stock list {agent_items} mismatches Ground Truth {gt_low_stock}."})
    else:
        details.append({"item": "Low stock items accuracy", "score": 0, "max_score": 40, "passed": False, "reason": "File missing or invalid."})

    # 4. LLM Semantic evaluation for report tone and precision specification (10 pts)
    if os.path.isfile(discrepancy_file):
        prompt = "Does the following text explicitly state that the number represents the TOTAL amount overcharged by 'CleanCorp', maintaining a professional yet clear tone?"
        if llm_judge_content(prompt, txt_content):
            details.append({"item": "LLM Semantic Check", "score": 10, "max_score": 10, "passed": True, "reason": "Text clearly and correctly states the intent."})
            total_score += 10
        else:
            details.append({"item": "LLM Semantic Check", "score": 0, "max_score": 10, "passed": False, "reason": "Text is ambiguous, incorrect, or lacks context."})
    else:
        details.append({"item": "LLM Semantic Check", "score": 0, "max_score": 10, "passed": False, "reason": "File missing."})

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
