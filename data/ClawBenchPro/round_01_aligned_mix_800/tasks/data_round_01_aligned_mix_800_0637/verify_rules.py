import os
import json
import glob

def verify():
    state = {
        "report_exists": False,
        "json_valid": False,
        "correct_high_risk_count": False,
        "filtered_future_dates": False,
        "average_score_correct": False
    }

    report_path = "audit_report/summary.json"
    # 尝试匹配该目录下任何json文件
    json_files = glob.glob("audit_report/*.json")
    if json_files:
        report_path = json_files[0]
        state["report_exists"] = True
        
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
                state["json_valid"] = True
                
                # 逻辑校验：
                # 原始高风险(score<40 且 日期有效): 
                # CASE_001 (35, valid), CASE_003 (20, valid), CASE_005 (39, valid)
                # CASE_006 (15, INVALID DATE)
                # 符合条件的 family 应为 ["Kim", "Smith", "Lee"]
                
                high_risk_families = data.get("high_risk_families", [])
                expected_families = ["Kim", "Smith", "Lee"]
                state["correct_high_risk_count"] = set(high_risk_families) == set(expected_families)
                
                # 剔除的错误记录数量应该是 2 (CASE_004, CASE_006)
                invalid_count = data.get("invalid_records_count", 0)
                state["filtered_future_dates"] = (invalid_count == 2)
                
                # 平均分计算 (35 + 20 + 39) / 3 = 31.333
                avg_score = data.get("average_score", 0)
                if 31.3 < avg_score < 31.4:
                    state["average_score_correct"] = True
        except:
            state["json_valid"] = False

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
