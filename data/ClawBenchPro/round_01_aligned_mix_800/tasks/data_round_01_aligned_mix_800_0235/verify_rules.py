import os
import json

def verify():
    report_path = "reports/market_plan.json"
    state = {
        "report_exists": False,
        "correct_items_included": False,
        "expired_items_excluded": False,
        "certified_only": False,
        "total_cost_correct": False,
        "avoided_trap_skill": True # 默认为 True，如果在 trace 中发现调用了错误的 skill 且没切换，则扣分
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            
            # 合格品：
            # 1. Local Honey (12*10=120) - V-1102 是 Gold
            # 2. Sustainable Oats (3.5*20=70) - V-2201 是 Silver
            # 总计: 190.0
            
            items = data.get("items", [])
            item_names = [i.get("name", i.get("item_name", "")) for i in items]
            
            state["correct_items_included"] = "Local Honey" in item_names and "Sustainable Oats" in item_names
            state["expired_items_excluded"] = "Organic Apples" not in item_names and "Organic Berries" not in item_names
            state["certified_only"] = "Plastic Bottled Soda" not in item_names
            
            total_cost = data.get("total_cost", 0)
            if abs(total_cost - 190.0) < 0.1:
                state["total_cost_correct"] = True
        except:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
