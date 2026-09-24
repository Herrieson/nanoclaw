import os
import sys
import json

def run_reference_logic(file_path):
    """
    参考实现逻辑：解析原始 L2 数据并找出首个有效的买卖盘倒挂。
    """
    max_ts = -1
    result = None

    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split('\x01')
            if len(parts) != 4:
                continue
            
            try:
                ts = int(parts[0])
                symbol = parts[1]
                bids_str = parts[2]
                asks_str = parts[3]
            except ValueError:
                continue

            # 严格单调递增检查
            if ts <= max_ts:
                continue
            max_ts = ts

            # 解析买盘最优价 (Bid[0])
            try:
                best_bid = float(bids_str.split('|')[0].split(':')[0])
                best_ask = float(asks_str.split('|')[0].split(':')[0])
            except (IndexError, ValueError):
                continue

            # 检查买卖盘倒挂 (Crossed Book)
            if best_bid >= best_ask:
                result = {"symbol": symbol, "timestamp": ts}
                break # 找到第一个符合条件的即可
    return result

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_json_path = os.path.join(workspace, "ops/target_replay.json")
    raw_data_path = os.path.join(workspace, "snapshots/l2_orderbook.dat")
    
    score = 0
    details = []

    # 1. 检查目标文件是否存在 (10分)
    if os.path.exists(target_json_path):
        score += 10
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 ops/target_replay.json 已生成"})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 ops/target_replay.json 未找到"})
        # 写入最终结果并提前退出
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 2. 检查 JSON 格式及字段 (20分)
    agent_data = {}
    try:
        with open(target_json_path, "r") as f:
            agent_data = json.load(f)
        score += 10
        details.append({"item": "JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        
        # 检查是否包含核心字段（允许大小写差异，但必须逻辑清晰）
        keys = [k.lower() for k in agent_data.keys()]
        if any("symbol" in k for k in keys) and any("timestamp" in k for k in keys):
            score += 10
            details.append({"item": "核心字段检查", "score": 10, "max_score": 10, "passed": True, "reason": "包含 symbol 和 timestamp 相关字段"})
        else:
            details.append({"item": "核心字段检查", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少必要字段，当前包含: {list(agent_data.keys())}"})
    except Exception as e:
        details.append({"item": "JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"解析失败: {str(e)}"})

    # 3. 核心逻辑验证 (70分)
    gold_standard = run_reference_logic(raw_data_path)
    if not gold_standard:
        details.append({"item": "数据源验证", "score": 0, "max_score": 70, "passed": False, "reason": "无法从原始数据中计算出参考答案，请检查环境"})
    else:
        agent_symbol = None
        agent_ts = None
        # 模糊匹配 Key
        for k, v in agent_data.items():
            if "symbol" in k.lower(): agent_symbol = v
            if "timestamp" in k.lower() or "ts" in k.lower(): agent_ts = v

        if str(agent_symbol) == str(gold_standard["symbol"]) and str(agent_ts) == str(gold_standard["timestamp"]):
            score += 70
            details.append({"item": "计算结果准确性", "score": 70, "max_score": 70, "passed": True, "reason": "成功定位到唯一的有效倒挂记录：FAT_FINGER_X"})
        elif str(agent_symbol) == "TRAP_SYM":
            score += 20
            details.append({"item": "计算结果准确性", "score": 20, "max_score": 70, "passed": False, "reason": "错误！Agent 抓取了被时间戳倒挂过滤掉的陷阱数据 (TRAP_SYM)"})
        else:
            details.append({"item": "计算结果准确性", "score": 0, "max_score": 70, "passed": False, "reason": f"结果不匹配。期望: {gold_standard}, 实际: {agent_data}"})

    # 写入最终总分
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
