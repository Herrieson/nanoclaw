import os
import sys
import json
import csv
import glob
import math

def calculate_ground_truth(workspace):
    # 1. Parse official roster and revoked list
    official_roster_path = os.path.join(workspace, "church_records/registry/2023_official_roster.txt")
    revoked_list_path = os.path.join(workspace, "church_records/registry/2023_revoked_list.txt")
    
    with open(official_roster_path, 'r', encoding='utf-8') as f:
        official_members = set(line.strip() for line in f if line.strip())
        
    with open(revoked_list_path, 'r', encoding='utf-8') as f:
        revoked_members = set(line.strip() for line in f if line.strip())
        
    valid_members = official_members - revoked_members
    
    # 2. Parse shifts
    unauthorized_workers = set()
    shift_files = glob.glob(os.path.join(workspace, "fair_management/shifts/**/*.csv"), recursive=True) + \
                  glob.glob(os.path.join(workspace, "fair_management/shifts/**/*.log"), recursive=True)
                  
    for file_path in shift_files:
        if not os.path.isfile(file_path):
            continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header or len(header) < 2:
                    continue # Skip noise logs masquerading as csv
                for row in reader:
                    if len(row) >= 2:
                        name = row[1].strip()
                        if name and name not in valid_members and name != "Name":
                            unauthorized_workers.add(name)
        except Exception:
            pass

    # 3. Parse catalog
    catalog_path = os.path.join(workspace, "inventory/catalog.json")
    pioneer_codes = set()
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog_data = json.load(f)
        for item in catalog_data:
            if item.get("collection_type") == "1800s_Pioneer":
                pioneer_codes.add(item.get("item_code"))
                
    # 4. Calculate total revenue
    total_revenue = 0.0
    receipt_files = glob.glob(os.path.join(workspace, "financials/receipts/**/*.json"), recursive=True)
    for file_path in receipt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                receipt = json.load(f)
                # Ignore test/noise json
                if "voided" not in receipt or "items" not in receipt:
                    continue
                if receipt["voided"] is True:
                    continue
                for item in receipt["items"]:
                    if item.get("code") in pioneer_codes:
                        qty = item.get("qty", 0)
                        price = item.get("unit_price", 0.0)
                        total_revenue += (qty * price)
        except Exception:
            pass

    return unauthorized_workers, round(total_revenue, 2)


def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score = 0
    details = []
    
    results_dir = os.path.join(workspace, "results")
    
    # Check if results directory exists
    if not os.path.isdir(results_dir):
        details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到名为 'results' 的目录"})
        write_score(0, details)
        return
        
    details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "已找到 'results' 目录"})
    score += 10
    
    # Find JSON file in results
    json_files = glob.glob(os.path.join(results_dir, "*.json"))
    if not json_files:
        details.append({"item": "检查结果文件", "score": 0, "max_score": 10, "passed": False, "reason": "'results' 目录中没有 JSON 文件"})
        write_score(score, details)
        return
        
    details.append({"item": "检查结果文件", "score": 10, "max_score": 10, "passed": True, "reason": "已找到结果 JSON 文件"})
    score += 10
    
    # Parse the first JSON file
    result_file = json_files[0]
    try:
        with open(result_file, 'r', encoding='utf-8') as f:
            agent_data = json.load(f)
    except Exception as e:
        details.append({"item": "检查结果 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"无法解析 JSON 文件: {str(e)}"})
        write_score(score, details)
        return
        
    details.append({"item": "检查结果 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
    score += 10
    
    # Calculate ground truth
    gt_workers, gt_revenue = calculate_ground_truth(workspace)
    
    # Extract data from agent JSON using heuristics (since key names aren't strict)
    agent_workers = None
    agent_revenue = None
    
    for k, v in agent_data.items():
        if isinstance(v, list) and all(isinstance(x, str) for x in v):
            agent_workers = set(v)
        if isinstance(v, (int, float)):
            agent_revenue = float(v)
            
    # Evaluate unauthorized workers (35 points)
    if agent_workers is not None:
        missing = gt_workers - agent_workers
        extra = agent_workers - gt_workers
        if not missing and not extra:
            details.append({"item": "核对未授权人员名单", "score": 35, "max_score": 35, "passed": True, "reason": "未授权人员名单完全精确匹配"})
            score += 35
        else:
            partial_score = max(0, 35 - len(missing)*5 - len(extra)*5)
            details.append({"item": "核对未授权人员名单", "score": partial_score, "max_score": 35, "passed": partial_score > 0, "reason": f"名单存在偏差。缺失: {len(missing)}个, 多余: {len(extra)}个"})
            score += partial_score
    else:
        details.append({"item": "核对未授权人员名单", "score": 0, "max_score": 35, "passed": False, "reason": "JSON 中未找到有效的字符串列表字段"})
        
    # Evaluate total revenue (35 points)
    if agent_revenue is not None:
        if math.isclose(agent_revenue, gt_revenue, rel_tol=1e-4, abs_tol=0.02):
            details.append({"item": "核对先锋物品总销售额", "score": 35, "max_score": 35, "passed": True, "reason": f"总销售额计算完全准确: {agent_revenue}"})
            score += 35
        else:
            details.append({"item": "核对先锋物品总销售额", "score": 0, "max_score": 35, "passed": False, "reason": f"总销售额不正确。Agent 值: {agent_revenue}, 真实值应为: {gt_revenue}"})
    else:
        details.append({"item": "核对先锋物品总销售额", "score": 0, "max_score": 35, "passed": False, "reason": "JSON 中未找到数值字段来表示销售额"})

    write_score(score, details)

def write_score(score, details):
    output = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
