import os
import json

def verify():
    results = {
        "report_exists": False,
        "json_valid": False,
        "skill_usage_check": False, # 是否成功通过 Skill 找到了 Ebony 的代码
        "total_value_correct": False,
        "dynamic_warning_correct": False
    }

    report_path = "deliverables/audit_report.json"
    
    if os.path.exists(report_path):
        results["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                results["json_valid"] = True
                
                # 计算逻辑验证：
                # DQ01 (Oak): 10 * 150 = 1500
                # UL02 (Maple): 8 * 320 = 2560
                # HD05 (Ebony): 2 * 6500 = 13000 (需要通过 Skill 找回代码)
                # OP04 (Mahogany): 12 * 450 = 5400
                # MH03 (Cedar): 15 * 120 = 1800
                # Total = 1500 + 2560 + 13000 + 5400 + 1800 = 24260
                
                total_val = data.get("total_value", 0)
                if abs(total_val - 24260) < 1:
                    results["total_value_correct"] = True
                
                # 检查是否识别了 Ebony 属于 HD05
                if "HD05" in str(data) or "Ebony" in str(data.get("valid_items", "")):
                    results["skill_usage_check"] = True

                # 检查动态预警 (Ebony 6500 应该触发，阈值通常在 5000-6000 波动)
                warnings = data.get("high_value_alerts", [])
                if any("Ebony" in str(w) for w in warnings):
                    results["dynamic_warning_correct"] = True
                    
        except Exception:
            results["json_valid"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    verify()
