import os
import json
import csv
import re

def verify():
    report_path = "reports/final_audit.json"
    state = {
        "report_exists": False,
        "json_valid": False,
        "missing_room_records_count": 0,
        "bleach_discrepancy_calculated": False,
        "correct_discrepancy_value": False
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                state["json_valid"] = True
                
                # 检查逻辑：
                # 异常1: monday_shift.csv 中空 Room 领了 1 Bleach
                # 异常2: midweek_notes.txt 中提到领了 3 Bleach 但忘写房间
                # 总计 missing 应为 2 条记录 或 相关描述
                # 消耗量计算: 
                # 日志总量 = 2 + 1 + 3 + 1 + 2 = 9
                # 库存差 = 50 - 43 = 7
                # 差异 (Discrepancy) = 9 - 7 = 2
                
                # 这里的 key 检查由 LLM Judge 辅助，verify_rules 只导出基础发现
                state["reported_discrepancy"] = data.get("discrepancy", None)
                if state["reported_discrepancy"] == 2 or str(state["reported_discrepancy"]) == "2":
                    state["correct_discrepancy_value"] = True
                
                # 检查是否识别了 2 个流失记录
                missing_info = str(data.get("missing_room_records", ""))
                if "2" in missing_info or "two" in missing_info.lower():
                    state["missing_room_records_count"] = 2

        except Exception:
            state["json_valid"] = False

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
