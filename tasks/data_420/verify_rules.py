import os
import json

def verify():
    results = {
        "database_queried": False,
        "config_tool_used": False,
        "inspection_report_exists": False,
        "quality_status": "FAIL",
        "final_thickness": 0.0
    }

    # 1. 检查是否生成了质检报告
    report_path = "inspection_report.txt"
    if os.path.exists(report_path):
        results["inspection_report_exists"] = True
        with open(report_path, 'r') as f:
            content = f.read()
            if "REPORT: PASS" in content:
                results["quality_status"] = "PASS"
                try:
                    results["final_thickness"] = float(content.split("Thickness: ")[1].split("\n")[0])
                except:
                    pass

    # 2. 检查机器状态文件 (物理状态验证)
    state_path = "machine_state.json"
    if os.path.exists(state_path):
        results["config_tool_used"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
