import os
import json

def verify():
    state = {
        "report_exists": False,
        "json_valid": False,
        "correct_high_risk": False,
        "external_flags_correct": False,
        "date_cleaning_correct": False,
        "skill_usage_check": False
    }

    report_path = "audit_report/summary.json"
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
                state["json_valid"] = True
                
                # 1. 高风险校验 (Kim, Smith, Lee)
                # Kim (Score 35 < 40), Smith (Score 20 < 40), Lee (Score 39 < 40)
                # Muller Score 42 > 40, 且无 audio 触发 risk_index > 0.7
                expected_high_risk = ["Kim", "Smith", "Lee"]
                actual_high_risk = data.get("high_risk_families", [])
                state["correct_high_risk"] = set(expected_high_risk) == set(actual_high_risk)
                
                # 2. 外部记录 (基于 v2_registry_search)
                # 根据 Mock 逻辑，Smith 应该是唯一能搜到 History 的（逻辑见 skill）
                state["external_flags_correct"] = (data.get("external_flags") == 1)
                
                # 3. 日期清洗 (Chen 2025, Patel 2026 是无效的)
                state["date_cleaning_correct"] = (data.get("invalid_records_count") == 2)
        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
