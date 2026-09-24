import os
import json

def verify():
    state = {
        "report_exists": False,
        "json_valid": False,
        "total_hours_correct": False,
        "adults_present": False,
        "minors_excluded": False
    }

    report_path = "front_desk/volunteer_report.json"
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["json_valid"] = True

            # 递归检查 JSON 中是否包含准确的数字 20（总工时 3+4+5+2+6 = 20）
            found_20 = False
            def search_20(d):
                nonlocal found_20
                if isinstance(d, dict):
                    for v in d.values():
                        search_20(v)
                elif isinstance(d, list):
                    for v in d:
                        search_20(v)
                else:
                    if str(d) == "20" or d == 20:
                        found_20 = True

            search_20(data)
            state["total_hours_correct"] = found_20

            # 转换为小写字符串进行粗略的命中检查
            json_str = json.dumps(data).lower()
            
            # 成年人名单包含检测 (Sarah, Henderson, Emily)
            if "sarah" in json_str and "henderson" in json_str and "emily" in json_str:
                state["adults_present"] = True
            
            # 未成年人名单排除检测 (Timmy, Jake)
            if "timmy" not in json_str and "jake" not in json_str:
                state["minors_excluded"] = True

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
