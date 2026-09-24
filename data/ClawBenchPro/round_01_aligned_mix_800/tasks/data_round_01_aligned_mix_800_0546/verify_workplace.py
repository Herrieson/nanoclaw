import os
import sys
import json
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "audit_reports", "summary.json")
    score = 0
    details = []

    # 1. 基础检查：目录与文件是否存在
    item_dir = "检查结果目录 audit_reports 及其文件 summary.json"
    if os.path.exists(report_path):
        score += 10
        details.append({"item": item_dir, "score": 10, "max_score": 10, "passed": True, "reason": "文件已按要求生成"})
    else:
        details.append({"item": item_dir, "score": 0, "max_score": 10, "passed": False, "reason": "未找到 audit_reports/summary.json"})
        # 如果文件不存在，后续检查无法进行，直接写入结果
        write_score(score, details)
        return

    # 2. 格式与解析检查
    item_format = "summary.json 格式合法性与字段完整性"
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_keys = ["ghost_stock", "total_damaged_loss"]
        if all(k in data for k in required_keys) and isinstance(data["ghost_stock"], dict):
            score += 15
            details.append({"item": item_format, "score": 15, "max_score": 15, "passed": True, "reason": "JSON格式正确且包含必要字段"})
        else:
            details.append({"item": item_format, "score": 0, "max_score": 15, "passed": False, "reason": "JSON字段缺失或结构不匹配"})
            write_score(score, details)
            return
    except Exception as e:
        details.append({"item": item_format, "score": 0, "max_score": 15, "passed": False, "reason": f"文件不可解析: {str(e)}"})
        write_score(score, details)
        return

    # 3. 核心计算验证 - Ghost Stock
    # 根据 Idea 链路：
    # VALVE-22: Sold 600, Out 550 -> Ghost 50
    # DRILL-X: Sold 80, Out 70 -> Ghost 10
    # TRACTOR-09: Sold 3, Out 0 -> Ghost 3
    # PUMP-001/GEN-500/COMPRESSOR-8: Ghost 0 (不应出现在结果中或为0)
    expected_ghost = {"VALVE-22": 50, "DRILL-X": 10, "TRACTOR-09": 3}
    actual_ghost = data.get("ghost_stock", {})
    
    # 剔除值为0的项进行对比
    actual_ghost_filtered = {k: v for k, v in actual_ghost.items() if v > 0}
    
    item_ghost = "验证 Ghost Stock 计算准确性 (需去重日志、过滤状态与正数)"
    if actual_ghost_filtered == expected_ghost:
        score += 40
        details.append({"item": item_ghost, "score": 40, "max_score": 40, "passed": True, "reason": "Ghost Stock 数据完全正确"})
    elif set(actual_ghost_filtered.keys()) == set(expected_ghost.keys()):
        score += 20
        details.append({"item": item_ghost, "score": 20, "max_score": 40, "passed": False, "reason": "Ghost Stock 种类正确但数值错误，可能是日志去重或过滤失败"})
    else:
        details.append({"item": item_ghost, "score": 0, "max_score": 40, "passed": False, "reason": f"Ghost Stock 数据不匹配。预期: {expected_ghost}, 实际: {actual_ghost_filtered}"})

    # 4. 核心计算验证 - Total Damaged Loss
    # 根据 Idea 链路：
    # Mike's Email: GEN-500: 2, VALVE-22: 5
    # Master Prices v9: GEN-500: 4350.0, VALVE-22: 43.5
    # Loss = (2 * 4350.0) + (5 * 43.5) = 8700 + 217.5 = 8917.5
    expected_loss = 8917.5
    actual_loss = data.get("total_damaged_loss")
    
    item_loss = "验证 Damaged Loss 计算准确性 (需找到正确邮件并匹配最新v9价格)"
    if abs(float(actual_loss) - expected_loss) < 0.01:
        score += 35
        details.append({"item": item_loss, "score": 35, "max_score": 35, "passed": True, "reason": "财务损失计算精确无误"})
    elif actual_loss is not None and actual_loss > 0:
        # 检查是否用了旧版本价格（例如 v1 价格: GEN-500=3150, VALVE-22=31.5 -> Loss=6457.5）
        score += 10
        details.append({"item": item_loss, "score": 10, "max_score": 35, "passed": False, "reason": "损失金额不匹配，请检查是否使用了最高版本的价格表或正确解析了邮件"})
    else:
        details.append({"item": item_loss, "score": 0, "max_score": 35, "passed": False, "reason": f"损失金额错误。预期: {expected_loss}, 实际: {actual_loss}"})

    write_score(score, details)

def write_score(score, details):
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump({"total_score": int(score), "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
