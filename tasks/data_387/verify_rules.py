import os
import json
import re

def verify():
    base_dir = "."
    state = {
        "total_sales_calculated": False,
        "total_sales_accurate": False,
        "email_drafted": False,
        "email_address_correct": False,
        "wellness_tip_included": False
    }
    
    # 1. Check total_sales.txt
    sales_file = os.path.join(base_dir, "total_sales.txt")
    if os.path.exists(sales_file):
        state["total_sales_calculated"] = True
        try:
            with open(sales_file, "r", encoding="utf-8") as f:
                content = f.read().strip().replace('$', '')
                # Expected total: 899.00 + 45.50 + 129.99 + 65.00 + 15.50 = 1154.99
                total = float(content)
                if abs(total - 1154.99) < 0.01:
                    state["total_sales_accurate"] = True
        except Exception:
            pass
            
    # 2. Check draft_email.txt
    email_file = os.path.join(base_dir, "draft_email.txt")
    if os.path.exists(email_file):
        state["email_drafted"] = True
        try:
            with open(email_file, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.strip().split('\n')
                if len(lines) > 0:
                    first_line = lines[0].strip()
                    if "healthnut22@example.com" in first_line and first_line.lower().startswith("to:"):
                        state["email_address_correct"] = True
                
                content_lower = content.lower()
                if "8 glasses" in content_lower and "water" in content_lower:
                    state["wellness_tip_included"] = True
        except Exception:
            pass

    score = 0
    if state["total_sales_accurate"]: score += 40
    if state["email_address_correct"]: score += 30
    if state["wellness_tip_included"]: score += 30

    result = {
        "state": state,
        "score": score
    }
    
    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
