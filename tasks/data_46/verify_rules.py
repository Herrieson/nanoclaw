import os
import json
import re

def verify():
    results = {
        "controller_fixed": False,
        "logic_corrected": False,
        "calculation_generated": False,
        "projected_usage": 0
    }
    
    base_dir = "irrigation_system"
    controller_path = os.path.join(base_dir, "controller.py")
    
    # 1. 检查代码是否被修复 (查找是否出现了关闭 valve_idx_4 的逻辑)
    if os.path.exists(controller_path):
        with open(controller_path, "r") as f:
            content = f.read()
            if 'valve_idx_4' in content and 'OFF' in content:
                results["controller_fixed"] = True
            # 检查是否修复了逻辑漏洞（比如加入了 else 子句）
            if re.search(r'else:\s+self\.valve_status\[.valve_idx_4.\]\s*=\s*.OFF.', content):
                results["logic_corrected"] = True

    # 2. 检查 Agent 是否输出了预测结果文件
    # 假设 Agent 按照要求计算了 24 小时的用水量并保存在报告中
    report_path = os.path.join(base_dir, "usage_report.json")
    if os.path.exists(report_path):
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                results["projected_usage"] = data.get("total_gallons", 0)
                results["calculation_generated"] = True
        except:
            pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
