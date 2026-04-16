import os
import json

def verify():
    base_path = "."
    results = {
        "script_fixed": False,
        "json_created": False,
        "correct_quantity": False,
        "correct_item": False
    }

    # 1. 检查脚本是否被尝试修复（通过修改时间或简单的语法检查，此处简化为检查运行结果）
    # 这里通过检查产物来反推
    
    # 2. 检查生成的 JSON 文件
    target_file = os.path.join(base_path, "pending_updates/fix_mole.json")
    if os.path.exists(target_file):
        results["json_created"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
                if data.get("item") == "Mole Poblano Sauce":
                    results["correct_item"] = True
                if str(data.get("quantity")) == "45":
                    results["correct_quantity"] = True
        except:
            pass

    # 3. 检查 script 是否能运行 (可选)
    
    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
