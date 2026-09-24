import os
import json
import pandas as pd

def verify():
    results = {
        "report_exists": False,
        "json_format_valid": False,
        "correct_staff_included": False,
        "math_accurate": False,
        "anomalies_detected": False
    }

    report_path = "reports/commission_audit.json"
    
    if os.path.exists(report_path):
        results["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            results["json_format_valid"] = True
            
            # 预期结果
            # Elena (S001): 10000*0.05 + 20000*0.025 = 1000
            # Kai (S002): 15000*0.05 = 750
            # Mele (S004): 10000*0.025 = 250
            # Luka (S003) and Admin (S005) must not exist
            
            names = [item.get("name") for item in data if "name" in item]
            correct_names = {"Elena Akana", "Kai Mana", "Mele Hina"}
            if set(names) == correct_names:
                results["correct_staff_included"] = True
            
            # 校验具体数值
            elena = next((i for i in data if i.get("name") == "Elena Akana"), {})
            kai = next((i for i in data if i.get("name") == "Kai Mana"), {})
            mele = next((i for i in data if i.get("name") == "Mele Hina"), {})
            
            if (elena.get("total_commission") == 1000 and 
                kai.get("total_commission") == 750 and 
                mele.get("total_commission") == 250):
                results["math_accurate"] = True
            
            # 校验异常
            anomalies = data.get("anomalies", [])
            if any("A-99" in str(a) for a in anomalies):
                results["anomalies_detected"] = True

        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
