import os
import sys
import json
import csv
from datetime import datetime

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "audit_reports/incident_summary.json")
    score = 0
    details = []

    # 1. Check file existence and basic JSON structure (10 points)
    if os.path.exists(report_path):
        data = load_json(report_path)
        if isinstance(data, list):
            score += 10
            details.append({"item": "文件格式校验", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且为JSON数组"})
        else:
            details.append({"item": "文件格式校验", "score": 0, "max_score": 10, "passed": False, "reason": "文件不是有效的JSON数组"})
            # Early exit if format is wrong
            save_score(score, details)
            return
    else:
        details.append({"item": "文件格式校验", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 audit_reports/incident_summary.json"})
        save_score(score, details)
        return

    # 2. Key Identification Accuracy (Targeting the 3 specific tainted deliveries)
    # Expected Targets: 
    # DEL-TRG-001: 08:15 (Alex), Casein
    # DEL-TRG-002: 15:22 (Morgan - covered), Lard, MSG
    # DEL-TRG-003: 20:45 (Jamie), Red 40
    
    expected_ids = {"DEL-TRG-001", "DEL-TRG-002", "DEL-TRG-003"}
    actual_ids = {item.get("delivery_id") for item in data if "delivery_id" in item}
    
    # Check for correct identification (30 points)
    correct_ids = expected_ids.intersection(actual_ids)
    id_score = len(correct_ids) * 10
    score += id_score
    details.append({"item": "正确识别违规订单ID", "score": id_score, "max_score": 30, "passed": len(correct_ids) == 3, "reason": f"找到了 {len(correct_ids)}/3 个目标订单"})

    # Check for false positives (noise/decoys) (20 points)
    # Common decoys: DEL-DCY-001 (REJECTED), DEL-DCY-002 (Wrong Date), DEL-DCY-003 (Tofu - not banned)
    decoys = {"DEL-DCY-001", "DEL-DCY-002", "DEL-DCY-003"}
    found_decoys = decoys.intersection(actual_ids)
    if len(found_decoys) == 0:
        score += 20
        details.append({"item": "排除干扰项", "score": 20, "max_score": 20, "passed": True, "reason": "未包含任何诱饵订单或错误日期/状态的订单"})
    else:
        details.append({"item": "排除干扰项", "score": 0, "max_score": 20, "passed": False, "reason": f"错误包含了诱饵订单: {found_decoys}"})

    # 3. Content Accuracy (Banned Ingredients and Managers) (40 points)
    # Expected Mapping
    expected_details = {
        "DEL-TRG-001": {"manager": "Alex", "ingredients": ["Casein"]},
        "DEL-TRG-002": {"manager": "Morgan", "ingredients": ["Lard", "MSG"]},
        "DEL-TRG-003": {"manager": "Jamie", "ingredients": ["Red 40"]}
    }

    content_score = 0
    for item in data:
        did = item.get("delivery_id")
        if did in expected_details:
            expected = expected_details[did]
            # Check manager (Crucial: Morgan covers Sam)
            mgr_match = item.get("manager") == expected["manager"]
            # Check ingredients (Must be list)
            ing_list = item.get("banned_ingredients", [])
            ing_match = set(ing_list) == set(expected["ingredients"])
            
            if mgr_match and ing_match:
                content_score += 10
            elif mgr_match or ing_match:
                content_score += 5
    
    # Bonus 10 points if all 3 are perfectly mapped
    if content_score == 30:
        content_score += 10
        details.append({"item": "经理与违禁品精确匹配", "score": 40, "max_score": 40, "passed": True, "reason": "所有订单的责任经理（含替班）和违禁品提取完全正确"})
    else:
        details.append({"item": "经理与违禁品精确匹配", "score": content_score, "max_score": 40, "passed": False, "reason": f"内容匹配得分: {content_score}/40。请检查Morgan替班逻辑或违禁品筛选逻辑。"})
    
    score += content_score
    save_score(score, details)

def save_score(score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": int(score), "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify_workplace()
