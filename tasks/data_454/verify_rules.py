import os
import json

def verify():
    results = {
        "final_json_exists": False,
        "json_content_correct": False,
        "salamander_fixed": False,
        "chart_script_exists": False,
        "total_species_count": 0
    }
    
    workspace = "./" # 执行环境
    json_path = os.path.join(workspace, "final_species_report.json")
    script_path = os.path.join(workspace, "generate_chart.py")
    
    # 1. 检查 JSON
    if os.path.exists(json_path):
        results["final_json_exists"] = True
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                results["total_species_count"] = len(data)
                
                # 检查 Ohio Blue Salamander 是否被修复 (正确学名为 Ambystoma laterale 或类似)
                # 只要不是 Error_Unknown_Species 且 包含 Ambystoma 关键字即可
                for item in data:
                    if "Ohio Blue Salamander" in item.get("common_name", ""):
                        if "Ambystoma" in item.get("scientific_name", ""):
                            results["salamander_fixed"] = True
                
                # 检查是否集成了所有来源（CSV, Partial JSON, DB）
                # 预期数量应为 2 (partial) + 2 (csv) + 2 (db) = 6
                if results["total_species_count"] >= 6:
                    results["json_content_correct"] = True
        except:
            pass

    # 2. 检查脚本
    if os.path.exists(script_path):
        results["chart_script_exists"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
