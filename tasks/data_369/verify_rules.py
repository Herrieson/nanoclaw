import os
import json

def verify():
    results = {
        "order_file_exists": False,
        "correct_sph_od": False,
        "correct_sph_os": False,
        "correct_refractive_index": False,
        "logic_fixed": False
    }
    
    output_path = "output/final_lab_order.json"
    
    if os.path.exists(output_path):
        results["order_file_exists"] = True
        try:
            with open(output_path, 'r') as f:
                data = json.load(f)
                
                # 校验点：
                # 原 OD sph -4.25, 规则是 add > 2.0 (2.25) 时 +0.12 -> -4.13
                # 原 OS sph -4.00, 规则是 add > 2.0 (2.25) 时 +0.12 -> -3.88
                # RI 应为 1.67
                
                if abs(data.get("final_prescriptions", {}).get("OD", {}).get("sph", 0) - (-4.13)) < 0.01:
                    results["correct_sph_od"] = True
                if abs(data.get("final_prescriptions", {}).get("OS", {}).get("sph", 0) - (-3.88)) < 0.01:
                    results["correct_sph_os"] = True
                if data.get("calculated_index") == 1.67:
                    results["correct_refractive_index"] = True
                    
                # 检查是否保留了原始 ID
                if data.get("target_id") == "#AB-2024-001":
                    results["logic_fixed"] = True
        except Exception:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
