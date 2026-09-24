import os
import json
import csv

def verify():
    results = {
        "report_exists": False,
        "json_valid": False,
        "total_value_correct": False,
        "invalid_items_found": False,
        "high_value_flagged": False
    }

    report_path = "deliverables/audit_report.json"
    
    # 1. 检查文件是否存在
    if os.path.exists(report_path):
        results["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                results["json_valid"] = True
                
                # 计算逻辑验证：
                # DQ01: 10 * 150 = 1500
                # UL02: 8 * 320 = 2560
                # HD05: 2 * 6000 = 12000
                # OP04: 12 * 450 = 5400
                # MH03: 15 * 120 = 1800
                # Total = 1500 + 2560 + 12000 + 5400 + 1800 = 23260
                
                # 检查总价值 (允许微小误差)
                total_val = data.get("total_value", 0)
                if abs(total_val - 23260) < 1:
                    results["total_value_correct"] = True
                
                # 检查不合规项目 (Pine 是 Wood/Received 但不在 CSV 里)
                invalid_list = data.get("invalid_items", [])
                if any("Pine" in str(item) for item in invalid_list):
                    results["invalid_items_found"] = True
                
                # 检查高价值标注 (ID_006 Ebony 6000 > 5000)
                high_val_notes = str(data.get("high_value_alerts", ""))
                if "Ebony" in high_val_notes or "6000" in high_val_notes:
                    results["high_value_flagged"] = True
                    
        except Exception:
            results["json_valid"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    verify()
