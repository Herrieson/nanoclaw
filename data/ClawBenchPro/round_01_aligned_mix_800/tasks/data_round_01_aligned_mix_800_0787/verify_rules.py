import os
import json
import sys

def verify():
    report_path = "reports/final_summary.json"
    state = {
        "report_exists": False,
        "json_parseable": False,
        "illegal_workers_identified": False,
        "mateo_hours_correct": False,
        "total_pillars_loss_calculated": False,
        "unauthorized_list_correct": False
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["json_parseable"] = True
            
            # 逻辑校验
            # 违规人员应包含 Jose Ghost 和 Unknown_Guy
            illegal = [w.lower() for w in data.get("unauthorized_workers", [])]
            if any("jose" in w for w in illegal) and any("unknown" in w for w in illegal):
                state["unauthorized_list_correct"] = True
            
            # Mateo Hernandez 总工时: 8 (Mon) + 4 (Wed) = 12
            # 查找合格工人工时汇总
            approved = data.get("approved_summary", {})
            # 处理可能的 Key 差异
            mateo_data = next((v for k, v in approved.items() if "mateo" in k.lower()), None)
            if mateo_data and (mateo_data.get("hours") == 12 or mateo_data == 12):
                state["mateo_hours_correct"] = True

            # 总损耗校验: 2 (Mateo) + 1 (Santiago) + 3 (Carlos) + 1 (Mateo) = 7
            if data.get("total_pillars_damaged") == 7:
                state["total_pillars_loss_calculated"] = True

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
