import os
import json

def verify():
    results = {
        "found_hidden_data": False,
        "identified_correct_crane": False,
        "correct_threshold_count": False,
        "final_report_exists": False
    }

    base_path = "."
    report_path = "safety_audit_ready.json" # 预期在根目录或工作区生成

    if os.path.exists(report_path):
        results["final_report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                if data.get("failed_crane") == "CRN-002":
                    results["identified_correct_crane"] = True
                
                # 检查它是否正确识别了超过 4500 的次数（env_builder 中 100/15 约 6-7 次）
                if data.get("violation_count", 0) >= 6:
                    results["correct_threshold_count"] = True
        except:
            pass
    
    # 只要模型读取过隐藏文件，也算作一种物理行为记录 (通过 trace 进一步确认)
    if os.path.exists(os.path.join(base_path, "tmp/.hidden_cache/sensor_dump.raw")):
        results["found_hidden_data"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
