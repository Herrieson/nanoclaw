import os
import sys
import json
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    catalog_path = os.path.join(workspace, "workspace/clean_catalog.json")
    cost_path = os.path.join(workspace, "workspace/amulet_cost.txt")
    
    score = 0
    details = []

    # 1. 检查目录和文件是否存在 (10 points)
    if os.path.exists(catalog_path):
        score += 5
        details.append({"item": "Existence: clean_catalog.json", "score": 5, "max_score": 5, "passed": True, "reason": "File found."})
    else:
        details.append({"item": "Existence: clean_catalog.json", "score": 0, "max_score": 5, "passed": False, "reason": "File not found."})

    if os.path.exists(cost_path):
        score += 5
        details.append({"item": "Existence: amulet_cost.txt", "score": 5, "max_score": 5, "passed": True, "reason": "File found."})
    else:
        details.append({"item": "Existence: amulet_cost.txt", "score": 0, "max_score": 5, "passed": False, "reason": "File not found."})

    # 2. 验证 clean_catalog.json 结构与数据准确性 (50 points)
    if os.path.exists(catalog_path):
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                catalog = json.load(f)
            
            # 基础结构检查
            if isinstance(catalog, dict) and "M_8472" in catalog:
                score += 10
                details.append({"item": "Catalog Structure", "score": 10, "max_score": 10, "passed": True, "reason": "Correct dict structure."})
                
                # 核心关键项的价格校验 (Min price logic & In Stock logic & Auth logic)
                # M_8472: Valid prices -> 4.50, 4.80. Out of stock -> 4.00. Fake -> 2.00. Correct: 4.50
                # M_1192: Correct: 1.20
                # M_3310: Correct: 0.75
                # M_9001: Correct: 15.00
                
                test_cases = [
                    ("M_8472", 4.50),
                    ("M_1192", 1.20),
                    ("M_3310", 0.75),
                    ("M_9001", 15.00)
                ]
                
                match_count = 0
                for mid, expected_price in test_cases:
                    if mid in catalog and abs(float(catalog[mid].get("price", 0)) - expected_price) < 0.001:
                        match_count += 1
                
                item_score = match_count * 10
                score += item_score
                details.append({
                    "item": "Catalog Accuracy (Core Materials)",
                    "score": item_score,
                    "max_score": 40,
                    "passed": match_count == 4,
                    "reason": f"Matched {match_count}/4 core material prices correctly."
                })
            else:
                details.append({"item": "Catalog Content", "score": 0, "max_score": 50, "passed": False, "reason": "Invalid JSON structure or missing key M_8472."})
        except Exception as e:
            details.append({"item": "Catalog Parsing", "score": 0, "max_score": 50, "passed": False, "reason": f"Error: {str(e)}"})
    else:
        details.append({"item": "Catalog Content", "score": 0, "max_score": 50, "passed": False, "reason": "File missing, skipping content check."})

    # 3. 验证 amulet_cost.txt 最终计算结果 (40 points)
    # Expected: (5*4.50) + (2*1.20) + (10*0.75) + (1*15.00) = 47.40
    if os.path.exists(cost_path):
        try:
            with open(cost_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Extract number
                match = re.search(r"(\d+\.\d+|\d+)", content)
                if match:
                    val = float(match.group(1))
                    if abs(val - 47.40) < 0.01:
                        score += 40
                        details.append({"item": "Final Cost Calculation", "score": 40, "max_score": 40, "passed": True, "reason": "Result is exactly 47.40."})
                    elif abs(val - 171.4) < 1.0: # Check if they used the wrong draft file (v2)
                        score += 10
                        details.append({"item": "Final Cost Calculation", "score": 10, "max_score": 40, "passed": False, "reason": "Result matched the DRAFT recipe instead of the FINAL one."})
                    else:
                        details.append({"item": "Final Cost Calculation", "score": 0, "max_score": 40, "passed": False, "reason": f"Incorrect value: {val}"})
                else:
                    details.append({"item": "Final Cost Calculation", "score": 0, "max_score": 40, "passed": False, "reason": "Could not find a numeric value in file."})
        except Exception as e:
            details.append({"item": "Cost File Parsing", "score": 0, "max_score": 40, "passed": False, "reason": f"Error: {str(e)}"})
    else:
        details.append({"item": "Final Cost Calculation", "score": 0, "max_score": 40, "passed": False, "reason": "File missing."})

    # Write results
    result = {
        "total_score": int(score),
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
