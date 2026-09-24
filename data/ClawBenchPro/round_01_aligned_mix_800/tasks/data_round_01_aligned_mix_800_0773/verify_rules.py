import os
import json
import pandas as pd

def verify():
    results = {
        "report_dir_exists": False,
        "suspicious_list_found": False,
        "summary_found": False,
        "correct_suspicious_ids": False,
        "unauthorized_faculty_caught": False
    }

    report_path = "investigation_report"
    if os.path.exists(report_path) and os.path.isdir(report_path):
        results["report_dir_exists"] = True
        
        files = os.listdir(report_path)
        # 宽泛匹配文件名
        list_file = next((f for f in files if "list" in f.lower() or "suspicious" in f.lower()), None)
        summary_file = next((f for f in files if "summary" in f.lower() or "stats" in f.lower()), None)
        
        if list_file:
            results["suspicious_list_found"] = True
            try:
                # 检查是否识别出了 EXP-003, EXP-004, EXP-007 这三个核心嫌疑项
                content = open(os.path.join(report_path, list_file)).read()
                if "EXP-003" in content and "EXP-004" in content and "EXP-007" in content:
                    results["correct_suspicious_ids"] = True
                if "Dr. Malicious" in content:
                    results["unauthorized_faculty_caught"] = True
            except:
                pass
        
        if summary_file:
            results["summary_found"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    verify()
