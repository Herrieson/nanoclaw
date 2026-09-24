import os
import json
import re

def verify():
    state = {
        "report_exists": False,
        "json_valid": False,
        "unauthorized_list_correct": False,
        "total_amount_correct": False,
        "excluded_misc_costs": False
    }

    report_path = "deliverables/audit_report.json"
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding='utf-8') as f:
                data = json.load(f)
                state["json_valid"] = True
                
                # 正确逻辑计算：
                # 合规人员：Alice Miller, Bob Chen, Sarah Jenkins, David Strauss, Linda Goldstein
                # 合规类别：Ingredients, Equipment
                # Alice: 150.50 (Ingredients)
                # Bob: 45.00 (Equipment) + 12.30 (Ingredients) = 57.30
                # Sarah: 88.20 (Ingredients)
                # Linda: 320.00 (Equipment)
                # David: (Misc - excluded)
                # 总计: 150.50 + 57.30 + 88.20 + 320.00 = 616.00
                
                # 不在名单里的人：Stranger Danger, Malicious User
                
                unauthorized = data.get("unauthorized_claimants", [])
                if isinstance(unauthorized, list):
                    names = set([n.lower() for n in unauthorized])
                    if "stranger danger" in names and "malicious user" in names:
                        state["unauthorized_list_correct"] = True
                
                total = data.get("total_approved_amount", 0)
                if abs(float(total) - 616.00) < 0.01:
                    state["total_amount_correct"] = True
                
                # 检查是否排除了 Parking Fee (15.00) 和 Apron (25.00)
                if state["total_amount_correct"]:
                    state["excluded_misc_costs"] = True
                    
        except Exception:
            state["json_valid"] = False

    with open("state.json", "w", encoding='utf-8') as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
