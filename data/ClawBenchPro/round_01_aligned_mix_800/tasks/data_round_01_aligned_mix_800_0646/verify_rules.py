import os
import json

def verify():
    results = {
        "security_alert_exists": False,
        "hours_report_exists": False,
        "intruders_identified_correctly": False,
        "total_hours_correct": False,
        "json_format_valid": False
    }

    alert_path = "deliverables/security_alert.txt"
    report_path = "deliverables/hours_report.json"

    # 1. 检查安全警报文件
    if os.path.exists(alert_path):
        results["security_alert_exists"] = True
        with open(alert_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            if "unknown intruder" in content and "bad actor" in content:
                results["intruders_identified_correctly"] = True

    # 2. 检查工时报告
    if os.path.exists(report_path):
        results["hours_report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                results["json_format_valid"] = True
                
                # 计算逻辑：
                # Maya: 3 + 2 = 5
                # Gordon: 3.5 + 1 = 4.5
                # Alice: 2
                # Julia: 3
                # Total: 14.5
                
                total = data.get("total_hours") or data.get("total")
                # 兼容不同键名，数值需匹配
                if total == 14.5:
                    results["total_hours_correct"] = True
        except:
            results["json_format_valid"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
