import os
import json
import sys

def verify():
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    leads_file = os.path.join(base_dir, "deliverables", "wellness_leads.txt")
    revenue_file = os.path.join(base_dir, "deliverables", "soil_monitor_revenue.txt")
    
    state = {
        "leads_file_exists": False,
        "revenue_file_exists": False,
        "leads_correct": False,
        "revenue_correct": False
    }
    
    # Check leads
    if os.path.exists(leads_file):
        state["leads_file_exists"] = True
        with open(leads_file, "r", encoding="utf-8") as f:
            content = f.read().lower()
            # Must contain alice, bob, diana. Must NOT contain charlie, edward, frank
            has_targets = all(email in content for email in ["alice@example.com", "bob@example.com", "diana@mail.com"])
            no_traps = all(email not in content for email in ["charlie@test.com", "edward@example.com", "frank@test.com"])
            if has_targets and no_traps:
                state["leads_correct"] = True

    # Check revenue
    if os.path.exists(revenue_file):
        state["revenue_file_exists"] = True
        with open(revenue_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            # 2*25 + 1*25 + 3*25 + 0*25 = 150
            if "150" in content and "1500" not in content:
                state["revenue_correct"] = True

    state_path = os.path.join(base_dir, "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
