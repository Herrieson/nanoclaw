import os
import json

def verify():
    report_path = "sustainability_audit_report.json"
    result = {
        "file_exists": False,
        "oil_audit_correct": False,
        "procurement_audit_correct": False,
        "format_valid": False
    }

    if os.path.exists(report_path):
        result["file_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                result["format_valid"] = True
                
                # 校验废油审计：周三和周五应该是异常日期
                anomalies = data.get("oil_anomalies", [])
                dates = [a.get("date") for a in anomalies]
                if "2023-10-04" in dates and "2023-10-06" in dates:
                    result["oil_audit_correct"] = True
                
                # 校验采购审计：
                # Total: 1200+3500+2800+1500+4000 = 13000
                # MN & Green: 1200 (V001) + 1500 (V003) = 2700
                # Ratio: 2700 / 13000 = 20.76%
                ratio = data.get("local_green_ratio", 0)
                if 0.20 <= ratio <= 0.21:
                    result["procurement_audit_correct"] = True
        except:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
