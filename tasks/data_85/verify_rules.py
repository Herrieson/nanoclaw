import os
import json
import re

def verify():
    results = {
        "file_created": False,
        "correct_oak_deficit": False,
        "correct_walnut_deficit": False,
        "unified_units_checked": False
    }
    
    report_path = "order_list.txt"
    if os.path.exists(report_path):
        results["file_created"] = True
        with open(report_path, "r") as f:
            content = f.read().lower()
            
            # 计算逻辑：
            # Oak (1x6x96): 10 (CSV) + 8 (Log) + 5 (Enc) = 23. Need 24. Deficit = 1.
            # Walnut (2x4x48): 5 (CSV) - 2 (Log Return) + 10 (Log) + 1 (Enc) = 14. Need 12. Deficit = 0.
            
            if "oak" in content and "1" in content:
                # 寻找特定的缺口数字
                if re.search(r"oak.*1", content):
                    results["correct_oak_deficit"] = True
            
            if "walnut" in content and "0" in content:
                if re.search(r"walnut.*0", content):
                    results["correct_walnut_deficit"] = True
                    
            if "inch" in content or "英寸" in content:
                results["unified_units_checked"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
