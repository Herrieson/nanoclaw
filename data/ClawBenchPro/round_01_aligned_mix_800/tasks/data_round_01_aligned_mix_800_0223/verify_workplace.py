import os
import json
import sys

def verify():
    state = {
        "report_dir_exists": False,
        "json_report_exists": False,
        "json_is_valid": False,
        "identified_avocados": False,
        "identified_truffle": False,
        "identified_saffron": False,
        "correct_total_missing_value": False
    }
    
    report_dir = "store_report"
    
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        state["report_dir_exists"] = True
        
        json_files = [f for f in os.listdir(report_dir) if f.endswith(".json")]
        if json_files:
            state["json_report_exists"] = True
            
            # 读取第一个找到的 json 文件
            report_path = os.path.join(report_dir, json_files[0])
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                state["json_is_valid"] = True
                
                # 序列化为全小写字符串，用于稳健的物理探测
                dumped_str = json.dumps(data).lower()
                
                if "avocado" in dumped_str:
                    state["identified_avocados"] = True
                if "truffle" in dumped_str:
                    state["identified_truffle"] = True
                if "saffron" in dumped_str:
                    state["identified_saffron"] = True
                    
                # 检查计算出的总损失金额是否正确 (135 或者 135.00)
                if "135" in dumped_str or "135.0" in dumped_str or "135.00" in dumped_str:
                    state["correct_total_missing_value"] = True
                    
            except Exception:
                pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
