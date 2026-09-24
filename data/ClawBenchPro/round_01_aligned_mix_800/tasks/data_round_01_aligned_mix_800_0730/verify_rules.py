import os
import json

def verify():
    results = {
        "suspects_file_exists": False,
        "report_file_exists": False,
        "correct_suspects_identified": False,
        "total_hours_correct": False,
        "report_structure_valid": False
    }

    # 1. 检查嫌疑人名单
    suspects_path = "suspects.txt"
    if os.path.exists(suspects_path):
        results["suspects_file_exists"] = True
        with open(suspects_path, "r") as f:
            content = f.read().lower()
            # 应该包含 Malicious User 和 Stranger_Danger
            if "malicious user" in content and "stranger_danger" in content:
                results["correct_suspects_identified"] = True

    # 2. 检查最终报告
    report_path = "deliverables/final_report.json"
    if os.path.exists(report_path):
        results["report_file_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                # 计算逻辑：
                # Aria (4.5) + Jordan (5.0) + Riley (6.5) + Alex (8.0) = 24.0
                # Casey (25.0) 和 Aria (15.0) 应该被过滤
                total = data.get("total_hours", 0)
                if abs(float(total) - 24.0) < 0.01:
                    results["total_hours_correct"] = True
                
                if "total_hours" in data and isinstance(data.get("details"), list):
                    results["report_structure_valid"] = True
        except:
            pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
