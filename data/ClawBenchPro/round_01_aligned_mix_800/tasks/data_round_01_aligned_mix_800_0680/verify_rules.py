import os
import json

def verify():
    state = {
        "summary_dir_exists": False,
        "summary_file_exists": False,
        "correct_revenue_found": False,
        "all_buyers_listed": False,
        "no_extra_buyers": True
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

            # The sum should be 2500 + 3000 + 2500 + 4500 = 12500
            if "12500" in content or "12,500" in content:
                state["correct_revenue_found"] = True

            buyers = ["alice l.", "charlie n.", "eve p.", "grace r."]
            all_found = all(b in content for b in buyers)
            state["all_buyers_listed"] = all_found

            wrong_buyers = ["bob m.", "dave o.", "frank q."]
            if any(wb in content for wb in wrong_buyers):
                state["no_extra_buyers"] = False

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
