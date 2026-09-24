import json

def optical_expense_analyzer_skill(base_cost, item_code, category):
    try:
        amount = float(base_cost)
        if category.lower() == "sustainable":
            # Apply 10% sustainability subsidy
            final_cost = round(amount * 0.9, 2)
        else:
            final_cost = amount
        
        return json.dumps({
            "item_code": item_code,
            "original_cost": amount,
            "final_cost": final_cost,
            "applied_subsidy": "10%" if category.lower() == "sustainable" else "0%"
        })
    except Exception as e:
        return f"Error: Invalid input parameters. {str(e)}"
