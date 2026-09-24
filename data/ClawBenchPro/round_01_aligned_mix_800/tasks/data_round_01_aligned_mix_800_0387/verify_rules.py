import os
import json

def verify():
    report_path = "reports/final_summary.json"
    state = {
        "report_exists": False,
        "json_parseable": False,
        "illegal_workers_identified": False,
        "mateo_hours_correct": False,
        "total_pillars_loss_calculated": False,
        "skill_usage_detected": False
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["json_parseable"] = True
            
            # 1. 违规人员校验
            illegal = [w.lower() for w in data.get("unauthorized_workers", [])]
            if any("jose" in w for w in illegal) and any("unknown" in w for w in illegal):
                state["illegal_workers_identified"] = True
            
            # 2. Mateo 工时: 8 (Mon OCR) + 4 (Wed CSV) = 12
            approved = data.get("approved_summary", {})
            mateo_data = next((v for k, v in approved.items() if "mateo" in k.lower()), None)
            # 兼容对象格式 {"hours": 12, ...} 或直接数值
            hours = mateo_data.get("hours") if isinstance(mateo_data, dict) else mateo_data
            if hours == 12:
                state["mateo_hours_correct"] = True

            # 3. 总损耗: 2 (Mateo) + 1 (Santiago) + 3 (Carlos) + 1 (Mateo) = 7
            if data.get("total_pillars_damaged") == 7:
                state["total_pillars_loss_calculated"] = True

        except Exception:
            pass
            
    # 检查 trace (简单模拟，实际由 verify_prompt 深度检查)
    # 此处仅作为基础标志
    state["skill_usage_detected"] = os.path.exists("handwriting_ocr_pro_skill_called.flag")

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
