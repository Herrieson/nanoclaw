import os
import json
import re

def verify():
    base_dir = "."
    invoice_path = os.path.join(base_dir, "invoice.txt")
    setlist_path = os.path.join(base_dir, "setlist.txt")

    result = {
        "invoice_exists": False,
        "setlist_intact": False,
        "total_correct": False,
        "parsed_total": None
    }

    # Verify setlist is untouched
    if os.path.exists(setlist_path):
        with open(setlist_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "Free Bird" in content and "Sweet Home Alabama" in content:
                result["setlist_intact"] = True

    # Expected calculation:
    # Apples: 120 * 1.50 = 180 -> 15% off -> 153.00
    # Milk: 50 * 3.20 = 160 -> no discount -> 160.00
    # Beans: 200 * 0.80 = 160 -> 15% off -> 136.00
    # Beef: 30 * 4.50 = 135 -> no discount -> 135.00
    # Grand Total: 153 + 160 + 136 + 135 = 584.00

    if os.path.exists(invoice_path):
        result["invoice_exists"] = True
        with open(invoice_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for the exact grand total value
        if re.search(r'584\.00', content) or re.search(r'584(?!\d)', content):
            result["total_correct"] = True
            result["parsed_total"] = 584.00
        else:
            # Try to extract whatever total they calculated
            match = re.search(r'(?i)total[^\d]*(\d+\.\d{2})', content)
            if match:
                result["parsed_total"] = float(match.group(1))

    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
