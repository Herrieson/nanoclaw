import os
import sqlite3
import json

def verify():
    base_path = "."
    results = {
        "script_fixed": False,
        "application_generated": False,
        "correct_agency_identified": False,
        "traditional_context_included": False
    }

    # 1. 检查脚本是否被修复
    try:
        # 尝试运行修复后的脚本（模拟环境）
        # 这里仅检查文件内容是否被修改且不再包含原始错误
        with open(os.path.join(base_path, "process_herbs.py"), "r") as f:
            content = f.read()
            if "sqlite3.connect" in content and "Oshá" in content and "name" in content:
                results["script_fixed"] = True
    except:
        pass

    # 2. 检查生成的申请书
    app_path = os.path.join(base_path, "permit_application.txt")
    if os.path.exists(app_path):
        results["application_generated"] = True
        with open(app_path, "r") as f:
            app_content = f.read().lower()
            if "az_compliance@epa.gov" in app_content:
                results["correct_agency_identified"] = True
            if "traditional" in app_content or "apache" in app_content:
                results["traditional_context_included"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
