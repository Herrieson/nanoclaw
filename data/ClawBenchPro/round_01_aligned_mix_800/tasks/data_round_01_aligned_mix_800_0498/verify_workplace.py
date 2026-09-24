import os
import sys
import json
import csv
import math

def get_ground_truth(workspace):
    rules_path = os.path.join(workspace, "procurement/rules.json")
    with open(rules_path, "r", encoding="utf-8") as f:
        rules = json.load(f)
    exchange_rates = rules["exchange_rates"]
    premium_tags = set(rules["premium_tags"])
    premium_multiplier = rules["premium_fee_multiplier"]

    registry_path = os.path.join(workspace, "procurement/vendor_registry.csv")
    approved_vendors = set()
    with open(registry_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["status"] == "APPROVED":
                approved_vendors.add(row["vendor_id"])

    total_cost = 0.0
    flagged = set()

    quotes_dir = os.path.join(workspace, "quotes")
    for vid in approved_vendors:
        vdir = os.path.join(quotes_dir, vid)
        if not os.path.isdir(vdir):
            continue
        for fname in os.listdir(vdir):
            if fname.startswith("final_quote") and (fname.endswith(".json") or fname.endswith(".csv")):
                fpath = os.path.join(vdir, fname)
                if fname.endswith(".json"):
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for item in data:
                            total_cost += process_item(item, exchange_rates, premium_tags, premium_multiplier, flagged)
                else:
                    with open(fpath, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            item = {
                                "item_name": row["item_name"],
                                "base_price": float(row["base_price"]),
                                "current_price": float(row["current_price"]),
                                "currency": row["currency"],
                                "tags": row["tags"].split("|") if row["tags"] else []
                            }
                            total_cost += process_item(item, exchange_rates, premium_tags, premium_multiplier, flagged)
    
    return total_cost, flagged

def process_item(item, rates, prem_tags, prem_mult, flagged):
    name = item["item_name"]
    bp = float(item["base_price"])
    cp = float(item["current_price"])
    curr = item["currency"]
    tags = item["tags"]

    # Spike check
    if cp > bp * 1.15:
        flagged.add(name)

    # Cost calculation
    cost = cp * rates.get(curr, 1.0)
    if any(t in prem_tags for t in tags):
        cost *= prem_mult
    
    return cost

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    target_file = os.path.join(workspace, "financial_forecast", "dinner_budget.json")
    
    # 1. 检查文件是否存在
    if not os.path.exists(target_file):
        score_details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 financial_forecast/dinner_budget.json"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=4)
        return
    else:
        score_details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
        
    # 2. 检查文件格式
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            agent_data = json.load(f)
        score_details.append({"item": "检查文件是否为合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "检查文件是否为合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=4)
        return

    # 3. 检查键是否存在
    if "total_usd_cost" not in agent_data or "flagged_items" not in agent_data:
        score_details.append({"item": "检查必要字段是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺失 total_usd_cost 或 flagged_items 字段"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=4)
        return
    else:
        score_details.append({"item": "检查必要字段是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "必要字段存在"})
        total_score += 10

    # Calculate Ground Truth
    gt_total_cost, gt_flagged = get_ground_truth(workspace)
    
    agent_cost = agent_data.get("total_usd_cost", 0.0)
    agent_flagged = set(agent_data.get("flagged_items", []))
    
    # 4. 验证 flagged_items (35分)
    extra_items = agent_flagged - gt_flagged
    missing_items = gt_flagged - agent_flagged
    
    if len(extra_items) == 0 and len(missing_items) == 0:
        score_details.append({"item": "验证 flagged_items 集合", "score": 35, "max_score": 35, "passed": True, "reason": "完全匹配"})
        total_score += 35
    else:
        error_count = len(extra_items) + len(missing_items)
        deduction = error_count * 5
        earned_score = max(0, 35 - deduction)
        passed = (earned_score == 35)
        score_details.append({"item": "验证 flagged_items 集合", "score": earned_score, "max_score": 35, "passed": passed, "reason": f"多了 {len(extra_items)} 个, 少了 {len(missing_items)} 个"})
        total_score += earned_score

    # 5. 验证 total_usd_cost (35分)
    try:
        agent_cost_float = float(agent_cost)
        diff = abs(agent_cost_float - gt_total_cost)
        # 允许极小的浮点误差
        if diff < 0.1:
            score_details.append({"item": "验证 total_usd_cost 准确性", "score": 35, "max_score": 35, "passed": True, "reason": "金额计算完全准确"})
            total_score += 35
        elif diff < 10.0:
            score_details.append({"item": "验证 total_usd_cost 准确性", "score": 15, "max_score": 35, "passed": False, "reason": f"金额有小幅误差, GT={gt_total_cost}, Agent={agent_cost_float}"})
            total_score += 15
        else:
            score_details.append({"item": "验证 total_usd_cost 准确性", "score": 0, "max_score": 35, "passed": False, "reason": f"金额计算错误, GT={gt_total_cost}, Agent={agent_cost_float}"})
    except ValueError:
        score_details.append({"item": "验证 total_usd_cost 准确性", "score": 0, "max_score": 35, "passed": False, "reason": "金额格式错误，无法转为浮点数"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=4)

if __name__ == "__main__":
    main()
