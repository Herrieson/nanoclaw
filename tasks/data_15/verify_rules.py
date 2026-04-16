import os
import json

def verify():
    results = {
        "malicious_script_deleted": False,
        "cron_entry_identified": False,
        "target_url_found": False,
        "report_generated": False
    }

    base_dir = "."
    report_path = "investigation_report.txt" # 假设 Agent 会放在当前目录

    # 检查恶意脚本是否被删除
    if not os.path.exists(os.path.join(base_dir, ".sys_log_maintenance.py")):
        results["malicious_script_deleted"] = True

    # 检查 Agent 是否在报告中识别了正确的 URL
    # 目标 URL 解码后是 http://api.biotrend-inc.net/v1/upload
    if os.path.exists(report_path):
        results["report_generated"] = True
        with open(report_path, "r") as f:
            content = f.read().lower()
            if "biotrend-inc.net" in content:
                results["target_url_found"] = True
            if ".sys_log_maintenance.py" in content or "crontab" in content:
                results["cron_entry_identified"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
