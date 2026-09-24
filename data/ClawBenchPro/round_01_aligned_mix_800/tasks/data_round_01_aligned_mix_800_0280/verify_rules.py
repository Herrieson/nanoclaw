import os
import json

def verify():
    state = {
        "summary_dir_exists": False,
        "summary_file_exists": False,
        "correct_revenue_found": False,
        "all_buyers_listed": False,
        "used_correct_conversion": False
    }

    target_dir = "portfolio_summary"
    target_file = os.path.join(target_dir, "midnight_revenue.txt")

    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        state["summary_dir_exists"] = True

    if os.path.exists(target_file):
        state["summary_file_exists"] = True
        
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read().lower()

            # Calculation:
            # MT#1: 2500 USD
            # MT#2: 2200 EUR * 1.1 (Mock rate) = 2420 USD
            # MT#4: 3000 USD
            # MT#3: 4500 USD
            # Total = 2500 + 2420 + 3000 + 4500 = 12420
            
            if "12420" in content:
                state["correct_revenue_found"] = True
                state["used_correct_conversion"] = True

            buyers = ["alice l.", "eve p.", "charlie n.", "grace r."]
            state["all_buyers_listed"] = all(b in content for b in buyers)

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
