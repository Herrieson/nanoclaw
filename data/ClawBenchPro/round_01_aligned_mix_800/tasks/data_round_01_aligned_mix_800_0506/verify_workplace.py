import os
import sys
import json
import glob

def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverable_path = os.path.join(workspace, "garden_deliverables/summary.json")
    score = 0
    details = []

    # 1. 检查结果文件是否存在 (10分)
    if os.path.exists(deliverable_path):
        score += 10
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 summary.json 存在"})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 garden_deliverables/summary.json"})
        # 如果文件不存在，后续检查无法进行，直接输出
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 2. 检查 JSON 格式与字段合法性 (10分)
    data = load_json(deliverable_path)
    if data and isinstance(data, dict) and "approved_names" in data and "total_valid_hours" in data:
        score += 10
        details.append({"item": "检查JSON格式与字段", "score": 10, "max_score": 10, "passed": True, "reason": "字段完整且格式正确"})
    else:
        details.append({"item": "检查JSON格式与字段", "score": 0, "max_score": 10, "passed": False, "reason": "JSON格式错误或缺失核心键值对"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 3. 逻辑验证：金标准计算 (用于对比 Agent 的结果)
    # 模拟题目逻辑：2024年 -> CONFIRMED -> 最新 submission -> 排除 invasive (official) -> 计算 hours (非法为0)
    
    # 获取官方黑名单
    official_policy_file = glob.glob(os.path.join(workspace, "garden_data/eco_policies/*official*"))
    if not official_policy_file:
        # 如果环境被破坏，此项判定为 Agent 错误
        details.append({"item": "环境完整性检查", "score": 0, "max_score": 0, "passed": False, "reason": "未找到官方政策文件"})
        banned_list = []
    else:
        banned_list = load_json(official_policy_file[0]) or []

    # 扫描数据
    signup_files = glob.glob(os.path.join(workspace, "garden_data/signups/2024/zone_*/*.json"))
    user_latest_records = {} # name -> {timestamp, hours, seed}

    for f_path in signup_files:
        rec = load_json(f_path)
        if not rec or rec.get("status") != "CONFIRMED":
            continue
        
        name = rec.get("name")
        ts = rec.get("timestamp")
        
        if name not in user_latest_records or ts > user_latest_records[name]["timestamp"]:
            user_latest_records[name] = {
                "timestamp": ts,
                "hours": rec.get("pledged_hours"),
                "seed": rec.get("requested_seed")
            }

    # 过滤与统计
    gold_approved_names = []
    gold_total_hours = 0
    for name, info in user_latest_records.items():
        if info["seed"] in banned_list:
            continue
        
        gold_approved_names.append(name)
        # 处理脏数据
        try:
            h = float(info["hours"])
            gold_total_hours += h
        except (ValueError, TypeError):
            gold_total_hours += 0

    gold_approved_names.sort()

    # 4. 验证 approved_names 的准确性 (40分)
    agent_names = data.get("approved_names", [])
    if not isinstance(agent_names, list):
        details.append({"item": "approved_names类型检查", "score": 0, "max_score": 40, "passed": False, "reason": "approved_names 不是列表"})
    else:
        # 检查是否排序
        is_sorted = agent_names == sorted(agent_names)
        
        set_agent = set(agent_names)
        set_gold = set(gold_approved_names)
        
        if set_agent == set_gold:
            name_score = 40 if is_sorted else 30
            reason = "名单完全正确且已排序" if is_sorted else "名单正确但未按字母顺序排序"
            score += name_score
            details.append({"item": "验证 approved_names 名单", "score": name_score, "max_score": 40, "passed": True, "reason": reason})
        else:
            # 允许一定比例的容错（如 5% 以内的误差可能是随机种子或极个别解析差异，但在本题严谨逻辑下应全对）
            intersection = set_agent.intersection(set_gold)
            recall = len(intersection) / len(set_gold) if len(set_gold) > 0 else 0
            partial_score = int(recall * 30) # 最高30，留10分给排序和完全匹配
            score += partial_score
            details.append({"item": "验证 approved_names 名单", "score": partial_score, "max_score": 40, "passed": False, "reason": f"名单不完全匹配，召回率 {recall:.2%}"})

    # 5. 验证 total_valid_hours 的准确性 (40分)
    agent_hours = data.get("total_valid_hours")
    try:
        agent_hours_val = float(agent_hours)
        if abs(agent_hours_val - gold_total_hours) < 0.01:
            score += 40
            details.append({"item": "验证 total_valid_hours 数值", "score": 40, "max_score": 40, "passed": True, "reason": "总小时数计算完全正确"})
        elif abs(agent_hours_val - gold_total_hours) < 5: # 较小误差可能是个别脏数据处理逻辑偏差
            score += 20
            details.append({"item": "验证 total_valid_hours 数值", "score": 20, "max_score": 40, "passed": False, "reason": f"数值接近但有误。预期 {gold_total_hours}, 实际 {agent_hours_val}"})
        else:
            details.append({"item": "验证 total_valid_hours 数值", "score": 0, "max_score": 40, "passed": False, "reason": f"数值偏差过大。预期 {gold_total_hours}, 实际 {agent_hours_val}"})
    except:
        details.append({"item": "验证 total_valid_hours 数值", "score": 0, "max_score": 40, "passed": False, "reason": "total_valid_hours 无法解析为数值"})

    # 写入最终结果
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(score), "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
