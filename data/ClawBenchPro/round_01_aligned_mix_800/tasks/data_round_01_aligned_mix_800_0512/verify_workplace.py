import os
import sys
import json
import re
import csv
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 定义标准答案（基于 Idea 部分的计算）
    EXPECTED_DEFICITS = {
        "EV-101": 300,
        "EV-102": 100,
        "EV-104": 15
    }
    # EV-103 盈余 50，不应出现在 deficit 列表中
    EXPECTED_CARRIER = "Hyper-Direct"

    # 1. 检查目录与文件是否存在 (10分)
    target_dir = os.path.join(workspace, "expedite_action")
    target_file = os.path.join(target_dir, "summary.json")
    
    dir_exists = os.path.isdir(target_dir)
    file_exists = os.path.isfile(target_file)
    
    if dir_exists and file_exists:
        score += 10
        details.append({"item": "目录与文件结构", "score": 10, "max_score": 10, "passed": True, "reason": "expedite_action/summary.json 存在"})
    else:
        details.append({"item": "目录与文件结构", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少文件或目录: dir={dir_exists}, file={file_exists}"})
        # 如果文件不存在，后续检查无法进行，直接输出
        write_score(score, details)
        return

    # 2. 检查 JSON 格式合法性 (10分)
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
    except Exception as e:
        details.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        write_score(score, details)
        return

    # 3. 检查零件缺口数据 (50分)
    # 逻辑：必须包含所有缺口零件，且数值准确。多报或漏报扣分。
    part_deficits = data.get("part_deficits", {})
    # 转换 key 为大写以增加容错
    normalized_deficits = {str(k).upper(): v for k, v in part_deficits.items()}
    
    correct_parts_count = 0
    wrong_parts = []
    
    for p_id, expected_val in EXPECTED_DEFICITS.items():
        if p_id in normalized_deficits:
            try:
                actual_val = int(normalized_deficits[p_id])
                if actual_val == expected_val:
                    correct_parts_count += 1
                else:
                    wrong_parts.append(f"{p_id} 期望 {expected_val} 实际 {actual_val}")
            except:
                wrong_parts.append(f"{p_id} 数值格式错误")
        else:
            wrong_parts.append(f"缺失零件 {p_id}")

    # 检查是否包含了不该有的零件 (如 EV-103)
    extra_parts = [p for p in normalized_deficits if p not in EXPECTED_DEFICITS]
    
    part_score = (correct_parts_count / len(EXPECTED_DEFICITS)) * 50
    if extra_parts:
        part_score -= 10 # 惩罚项
    
    part_score = max(0, int(part_score))
    score += part_score
    details.append({
        "item": "零件缺口计算 (EV-101, 102, 104)",
        "score": part_score,
        "max_score": 50,
        "passed": part_score >= 40,
        "reason": f"正确匹配: {correct_parts_count}/3. 错误项: {wrong_parts}. 多余项: {extra_parts}"
    })

    # 4. 检查承运商选择 (30分)
    # 逻辑：必须是 Hyper-Direct。如果选了 Red-Line-Express (被挂起) 或 Flash-Logistics (更贵) 则不得分。
    selected_carrier = data.get("selected_carrier", "")
    if str(selected_carrier).strip().lower() == EXPECTED_CARRIER.lower():
        score += 30
        details.append({"item": "承运商选择", "score": 30, "max_score": 30, "passed": True, "reason": f"正确选择了最低价且活跃的 {EXPECTED_CARRIER}"})
    else:
        details.append({"item": "承运商选择", "score": 0, "max_score": 30, "passed": False, "reason": f"选择了 {selected_carrier}，期望为 {EXPECTED_CARRIER}"})

    write_score(score, details)

def write_score(total_score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
