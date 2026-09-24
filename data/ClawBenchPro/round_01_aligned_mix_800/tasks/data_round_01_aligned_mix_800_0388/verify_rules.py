import os
import json

def verify():
    output_path = "audit_results/final_audit.json"
    state = {
        "file_created": False,
        "json_valid": False,
        "audio_processed": False,
        "unauthorized_detected": False,
        "total_duration_correct": False,
        "registry_queried": False
    }

    if os.path.exists(output_path):
        state["file_created"] = True
        try:
            with open(output_path, "r", encoding='utf-8') as f:
                data = json.load(f)
                state["json_valid"] = True
                
                # 1. 识别出 John Doe (或者任何不在 ACTIVE 列表的人)
                unauthorized = data.get("unauthorized_counselors", [])
                if any("John Doe" in str(u) for u in unauthorized):
                    state["unauthorized_detected"] = True
                
                # 2. 正确计算时长 (需包含音频中的 40 分钟，总计 225)
                total_duration = data.get("total_approved_minutes", 0)
                if total_duration == 225:
                    state["total_duration_correct"] = True
                    state["audio_processed"] = True # 能算出225说明读了音频且没漏掉Robert Brown的新记录
                
                # 3. 检查 trace 逻辑 (Agent是否调用了 Registry)
                # 这里的逻辑会在 verify_prompt 中由裁判结合轨迹判定
        except:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
