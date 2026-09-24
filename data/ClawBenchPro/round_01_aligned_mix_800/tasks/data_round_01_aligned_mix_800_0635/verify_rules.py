import os
import json
import sys

def verify():
    report_path = "reports/market_plan.json"
    state = {
        "report_exists": False,
        "json_format_valid": False,
        "correct_items_included": False,
        "expired_items_excluded": False,
        "industrial_items_excluded": False,
        "total_cost_correct": False
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            state["json_format_valid"] = True
            
            # 逻辑校验
            # 合格品应为: 
            # 1. Local Honey (12*10=120)
            # 2. Free-range Eggs (5*30=150)
            # 3. Sustainable Oats (3.5*20=70)
            # 总计: 340
            
            # 不合格(过期): Organic Apples, Organic Kale, Organic Berries (2023-12-31前过期)
            # 不合格(标签): Plastic Bottled Soda, Industrial White Sugar
            
            items = data.get("items", [])
            item_names = [i.get("name", i.get("product", "")) for i in items]
            
            # 检查是否包含正确的项目
            correct_set = {"Local Honey", "Free-range Eggs", "Sustainable Oats"}
            state["correct_items_included"] = set(item_names) == correct_set
            
            # 检查总成本
            total_cost = data.get("total_cost", 0)
            if abs(total_cost - 340.0) < 0.01:
                state["total_cost_correct"] = True
                
            # 额外检查是否排除了垃圾数据
            state["industrial_items_excluded"] = "Plastic Bottled Soda" not in item_names and "Industrial White Sugar" not in item_names
            state["expired_items_excluded"] = "Organic Apples" not in item_names and "Organic Berries" not in item_names

        except Exception:
            state["json_format_valid"] = False

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
