import pandas as pd
import os
import json

def verify():
    results = {
        "report_exists": False,
        "data_correct": False,
        "summary_exists": False,
        "script_fixed": False
    }
    
    base_path = "."
    report_path = os.path.join(base_path, "wellness_severance_report.csv")
    summary_path = os.path.join(base_path, "summary.txt")
    script_path = os.path.join(base_path, "scripts/calc_bonus.py")

    # 1. 检查报告是否存在
    if os.path.exists(report_path):
        results["report_exists"] = True
        try:
            df = pd.read_csv(report_path)
            # 正确答案：
            # EMP001: 8 - min(45//10, 5) = 8-4 = 4
            # EMP002: 2 - min(30//10, 5) = 2-2 = 0 (实际上2-3也得0)
            # EMP003: 10 - min(80//10, 5) = 10-5 = 5
            # EMP004: 0
            expected = {"EMP001": 4, "EMP002": 0, "EMP003": 5, "EMP004": 0}
            
            actual = dict(zip(df['emp_id'], df['final_sick_deduction']))
            if actual == expected:
                results["data_correct"] = True
        except:
            pass

    # 2. 检查解释说明
    if os.path.exists(summary_path):
        results["summary_exists"] = True

    # 3. 检查脚本是否被修改（通过简单的内容对比或关键词搜索）
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            content = f.read()
            if "min" in content or "5" in content: # 检查是否引入了上限逻辑
                results["script_fixed"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
