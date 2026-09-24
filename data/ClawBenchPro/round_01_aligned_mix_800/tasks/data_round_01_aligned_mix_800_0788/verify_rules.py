import os
import json
import sys

def verify():
    output_path = "audit_results/final_audit.json"
    state = {
        "file_created": False,
        "json_valid": False,
        "unauthorized_detected": False,
        "total_duration_correct": False,
        "deduplication_performed": False
    }

    if os.path.exists(output_path):
        state["file_created"] = True
        try:
            with open(output_path, "r", encoding='utf-8') as f:
                data = json.load(f)
                state["json_valid"] = True
                
                # 检查逻辑
                # 1. 识别出 John Doe
                unauthorized = data.get("unauthorized_counselors", [])
                if any("John Doe" in str(u) for u in unauthorized):
                    state["unauthorized_detected"] = True
                
                # 2. 正确计算时长 (45+30+60+50 = 185)
                # 如果没有去重，计算 185 + 45 = 230，这里设阈值
                total_duration = data.get("total_approved_minutes", 0)
                if total_duration == 185:
                    state["total_duration_correct"] = True
                    state["deduplication_performed"] = True
                elif total_duration == 230:
                    state["total_duration_correct"] = False
                    state["deduplication_performed"] = False
        except:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
