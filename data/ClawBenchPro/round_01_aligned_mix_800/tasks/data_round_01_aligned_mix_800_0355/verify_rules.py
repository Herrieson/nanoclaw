import os
import json

def verify():
    state = {
        "deliverables_folder_exists": False,
        "vip_alerts_exists": False,
        "junk_count_exists": False,
        "vip_alerts_valid": False,
        "junk_count_correct": False
    }

    if os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True

    vip_alerts_path = os.path.join("deliverables", "vip_alerts.json")
    if os.path.exists(vip_alerts_path):
        state["vip_alerts_exists"] = True
        try:
            with open(vip_alerts_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            text_dump = json.dumps(data).lower()
            # 核心判断逻辑不变，Agent 必须成功查出并保存这三个人的物品，剔除大卫
            has_marcus = "marcus johnson" in text_dump and "jacket" in text_dump
            has_sarah = "sarah connor" in text_dump and "watch" in text_dump
            has_chloe = "chloe bennett" in text_dump and "vr" in text_dump
            has_david = "david smith" in text_dump 
            
            if has_marcus and has_sarah and has_chloe and not has_david:
                state["vip_alerts_valid"] = True
        except Exception:
            pass

    junk_count_path = os.path.join("deliverables", "junk_count.txt")
    if os.path.exists(junk_count_path):
        state["junk_count_exists"] = True
        try:
            with open(junk_count_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                # The correct count of junk (no specific owner) is 4:
                # dirty sock (NONE), keys (N/A), water bottle (blank), loose change (null)
                if content == "4" or " 4 " in f" {content} ":
                    state["junk_count_correct"] = True
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
