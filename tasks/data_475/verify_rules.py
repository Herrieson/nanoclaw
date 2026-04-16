import os
import re

def verify():
    report_path = "final_report.txt"
    results = {
        "report_exists": False,
        "correct_error_code": False,
        "correct_total_cost": False,
        "correct_timestamp": False
    }

    if os.path.exists(report_path):
        results["report_exists"] = True
        with open(report_path, "r") as f:
            content = f.read().upper()
            
            # 校验 P0171 故障码
            if "P0171" in content:
                results["correct_error_code"] = True
            
            # 校验总金额: 15.50 + 289.99 + (8.00 * 4) = 337.49
            if "337.49" in content:
                results["correct_total_cost"] = True
            
            # 校验时间戳 (14:35 或 2023-10-27)
            if "14:35" in content or "1698417322" in content:
                results["correct_timestamp"] = True

    return results

if __name__ == "__main__":
    import json
    res = verify()
    with open("verify_result.json", "w") as f:
        json.dump(res, f)
