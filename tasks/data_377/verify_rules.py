import os
import json
import re

def verify():
    work_dir = "."
    order_sheet_path = os.path.join(work_dir, "order_sheet.txt")
    
    state = {
        "order_sheet_exists": False,
        "correct_total_found": False,
        "items_mentioned": {
            "apples": False,
            "milk": False,
            "eggs": False,
            "honey": False,
            "oats": False,
            "almond butter": False
        },
        "incorrect_items_ordered": False,
        "extracted_total_line": ""
    }

    if os.path.exists(order_sheet_path):
        state["order_sheet_exists"] = True
        with open(order_sheet_path, "r", encoding="utf-8") as f:
            content = f.read()
            content_lower = content.lower()

        # Target total is 1181 or 1181.00
        # Check if 1181 is in the text
        if re.search(r'\b1181(\.00)?\b', content):
            state["correct_total_found"] = True

        # Check for required items (these had stock < 15)
        if "apple" in content_lower: state["items_mentioned"]["apples"] = True
        if "milk" in content_lower: state["items_mentioned"]["milk"] = True
        if "egg" in content_lower: state["items_mentioned"]["eggs"] = True
        if "honey" in content_lower: state["items_mentioned"]["honey"] = True
        if "oat" in content_lower: state["items_mentioned"]["oats"] = True
        if "almond butter" in content_lower: state["items_mentioned"]["almond butter"] = True

        # Check for items that should NOT be ordered (stock >= 15)
        if "bread" in content_lower or "carrot" in content_lower or "banana" in content_lower:
            state["incorrect_items_ordered"] = True

        # Try to grab the last few lines for context
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if lines:
            state["extracted_total_line"] = lines[-1]

    with open(os.path.join(work_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
