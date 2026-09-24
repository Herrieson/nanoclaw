import os
import sys
import json
import csv
import re
from pathlib import Path

def calculate_ground_truth(workspace):
    """
    根据 env_builder 的逻辑（固定 seed(42)）在验证脚本中复刻逻辑，得出绝对参考答案。
    """
    # 1. 加载 materials_catalog
    material_db = {}
    catalog_dir = Path(workspace) / "materials_catalog"
    if catalog_dir.exists():
        for csv_file in catalog_dir.glob("*.csv"):
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    material_db[row["Material_ID"]] = {"Name": row["Name"], "Category": row["Category"]}

    # 2. 加载 active_codes
    valid_codes = set()
    active_dir = Path(workspace) / "reference/active_codes"
    if active_dir.exists():
        for j_file in active_dir.glob("*.json"):
            with open(j_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                valid_codes.update(data.keys())

    # 3. 遍历 inventory 统计
    total_compliant_value = 0.0
    non_compliant_items = []
    alerts_over_5000 = []

    inventory_dir = Path(workspace) / "inventory"
    if inventory_dir.exists():
        for root, dirs, files in os.walk(inventory_dir):
            for filename in files:
                filepath = Path(root) / filename
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if not lines or lines[0].strip() != "APPROVED_BY: R.M.":
                            continue
                        
                        for line in lines[1:]:
                            if "TX:" not in line: continue
                            # 鲁棒的提取逻辑
                            parts = {}
                            for p in line.split('|'):
                                if ':' in p:
                                    k, v = p.split(':', 1)
                                    parts[k.strip()] = v.strip()
                            
                            tx_id = parts.get("TX")
                            mat_id = parts.get("MAT")
                            qty_str = parts.get("Q")
                            up_str = parts.get("UP")
                            stat = parts.get("STAT")

                            if not all([tx_id, mat_id, qty_str, up_str, stat]): continue
                            
                            if stat == "Received":
                                mat_info = material_db.get(mat_id)
                                if mat_info and mat_info["Category"] == "Wood":
                                    qty = float(qty_str)
                                    up = float(up_str)
                                    mat_name = mat_info["Name"]
                                    
                                    # 检查合规性
                                    if mat_name in valid_codes:
                                        total_compliant_value += qty * up
                                    else:
                                        non_compliant_items.append({"tx_id": tx_id, "material_name": mat_name})
                                    
                                    # 检查预警
                                    if up > 5000:
                                        alerts_over_5000.append({"tx_id": tx_id, "unit_price": up})
                except:
                    continue

    return {
        "total_compliant_value": total_compliant_value,
        "non_compliant_items": non_compliant_items,
        "alerts_over_5000": alerts_over_5000
    }

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = Path(workspace) / "deliverables/audit_report.json"
    
    score = 0
    details = []

    # 1. 文件存在性检查 (10分)
    if not report_path.exists():
        details.append({"item": "Audit report existence", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables/audit_report.json not found"})
    else:
        score += 10
        details.append({"item": "Audit report existence", "score": 10, "max_score": 10, "passed": True, "reason": "File exists"})

        # 2. 格式与解析检查 (10分)
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                agent_data = json.load(f)
            score += 10
            details.append({"item": "JSON format validation", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed successfully"})
            
            # 获取参考答案
            truth = calculate_ground_truth(workspace)

            # 3. 合规总价值检查 (30分)
            # 允许 0.01 的浮点误差
            agent_val = agent_data.get("total_compliant_value", -1)
            if abs(agent_val - truth["total_compliant_value"]) < 0.1:
                score += 30
                details.append({"item": "total_compliant_value check", "score": 30, "max_score": 30, "passed": True, "reason": "Calculated value matches ground truth"})
            else:
                details.append({"item": "total_compliant_value check", "score": 0, "max_score": 30, "passed": False, "reason": f"Expected {truth['total_compliant_value']}, got {agent_val}"})

            # 4. 不合规清单检查 (25分)
            # 检查集合是否匹配
            agent_nc = sorted([item.get("tx_id", "") for item in agent_data.get("non_compliant_items", [])])
            truth_nc = sorted([item["tx_id"] for item in truth["non_compliant_items"]])
            if agent_nc == truth_nc:
                score += 25
                details.append({"item": "non_compliant_items check", "score": 25, "max_score": 25, "passed": True, "reason": "TX list matches perfectly"})
            else:
                details.append({"item": "non_compliant_items check", "score": 0, "max_score": 25, "passed": False, "reason": f"Mismatch in non-compliant TX IDs. Expected count: {len(truth_nc)}"})

            # 5. 超5000预警检查 (25分)
            agent_alerts = sorted([item.get("tx_id", "") for item in agent_data.get("alerts_over_5000", [])])
            truth_alerts = sorted([item["tx_id"] for item in truth["alerts_over_5000"]])
            if agent_alerts == truth_alerts:
                score += 25
                details.append({"item": "alerts_over_5000 check", "score": 25, "max_score": 25, "passed": True, "reason": "High price alerts match perfectly"})
            else:
                details.append({"item": "alerts_over_5000 check", "score": 0, "max_score": 25, "passed": False, "reason": f"Mismatch in high-price TX IDs. Expected count: {len(truth_alerts)}"})

        except Exception as e:
            details.append({"item": "Content analysis", "score": 0, "max_score": 80, "passed": False, "reason": f"Error during parsing content: {str(e)}"})

    # 输出结果
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
