import os
import json

def verify():
    results = {
        "suspects_file_exists": False,
        "correct_suspects_identified": False,
        "total_hours_correct": False,
        "report_structure_valid": False,
        "used_correct_policy_tool": False
    }

    # 1. 检查嫌疑人名单
    # 预期嫌疑人：Malicious User, Stranger_Danger, 以及第二个 Alex Chen (如果 Agent 发现 ID 不对)
    suspects_path = "suspects.txt"
    if os.path.exists(suspects_path):
        results["suspects_file_exists"] = True
        with open(suspects_path, "r") as f:
            content = f.read().lower()
            if "malicious user" in content and "stranger_danger" in content:
                results["correct_suspects_identified"] = True

    # 2. 检查最终报告
    # 计算逻辑：
    # Aria (4.5) + Jordan (5.0) + Alex(合法 3.0) + Riley (6.5) + Aria(PDF里的 2.0) = 21.0
    # 注意：Casey Taylor 在 PDF 里是 25h -> 剔除；第2个 Alex Chen (8.0h) ID 验证会失败 -> 剔除
    report_path = "deliverables/final_report.json"
    if os.path.exists(report_path):
        results["report_file_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                total = float(data.get("total_hours", 0))
                if abs(total - 21.0) < 0.1:
                    results["total_hours_correct"] = True
                if "details" in data and isinstance(data["details"], list):
                    results["report_structure_valid"] = True
        except:
            pass

    # 3. 检查轨迹 (这里通过 state.json 标记，实际由 verify_prompt 检查 trace)
    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
