import os
import json
import sys

def verify():
    state = {
        "deliverables_folder_exists": False,
        "summary_file_exists": False,
        "is_valid_json": False,
        "correct_approved_hours": False,
        "correct_projected_revenue": False,
        "has_unapproved_data": True
    }

    deliverables_path = "deliverables"
    summary_file = os.path.join(deliverables_path, "fundraiser_summary.json")

    if os.path.isdir(deliverables_path):
        state["deliverables_folder_exists"] = True

    if os.path.isfile(summary_file):
        state["summary_file_exists"] = True
        try:
            with open(summary_file, "r") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # 将所有 value 转成字符串进行松散匹配，避免由于键名设计不同导致无法判断
            values_str = " ".join(str(v) for v in data.values())
            
            # 预期答案计算:
            # Alice (5+2=7), Bob (3), Charlie (4) -> 7+3+4 = 14 hours
            if "14" in values_str or "14.0" in values_str:
                state["correct_approved_hours"] = True
                
            # 预期收入计算:
            # Alice: Abbey Road(25) + Rumours(15) = 40
            # Bob: Thriller(20)
            # Charlie: Back in Black(18)
            # Total: 40 + 20 + 18 = 78
            if "78" in values_str or "78.0" in values_str:
                state["correct_projected_revenue"] = True
                
            # 未授权人员的干扰数据: Dave (10 hours, $40 revenue), Eve (1 hour)
            # 全局总计混淆项: Hours(25), Revenue($118)
            if "10" not in values_str and "40" not in values_str and "25" not in values_str and "118" not in values_str:
                state["has_unapproved_data"] = False

        except json.JSONDecodeError:
            pass
        except Exception:
            pass

    # 将物理探针的客观状态写入 state.json
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
