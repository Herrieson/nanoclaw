import sys
import json

def calculate_yield(item_id, quantity, rate):
    try:
        q = float(quantity)
        r = float(rate)
        days = round(q / r, 1) if r > 0 else 999
        return json.dumps({"item_id": item_id, "days_remaining": days, "status": "Urgent" if days < 7 else "Stable"})
    except Exception as e:
        return f"Error: Invalid input. {str(e)}"

if __name__ == "__main__":
    # Expecting: python skill.py CHEM_001 5 0.5
    if len(sys.argv) == 4:
        print(calculate_yield(sys.argv[1], sys.argv[2], sys.argv[3]))
