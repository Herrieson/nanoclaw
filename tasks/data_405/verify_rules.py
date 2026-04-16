import os
import pandas as pd
import json

def verify():
    results = {
        "file_exists": False,
        "correct_shifts_count": 0,
        "pete_investigation_correct": False,
        "data_integrity": False
    }
    
    file_path = "final_schedule.csv"
    if os.path.exists(file_path):
        results["file_exists"] = True
        try:
            df = pd.read_csv(file_path)
            # 预期班次：Mon-Sun 共 8-9 个条目（基于提示词和日志）
            # Mon: Sarah(AM), Tue: Mike(PM), Wed: Chloe(AM), Thu: Pete(AM), Fri: Sarah(PM), Sat: Pete(AM), Mike(PM), Sun: Chloe(AM), Sarah(PM)
            results["correct_shifts_count"] = len(df)
            
            # 检查关键数据
            if "Pete" in df.values and "Saturday" in df.values:
                results["data_integrity"] = True
        except:
            pass

    # 检查 Agent 是否在对话或文件中提到了 Pete 周三没来
    # 这部分通常结合 verify_prompt.md 由 LLM 判定，此处仅做基础检查
    results["pete_investigation_hint"] = os.path.exists("pete_report.txt") # 假设 Agent 可能会写报告

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
