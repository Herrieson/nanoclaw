import os
import json

def verify():
    state = {
        "file_exists": False,
        "valid_json": False,
        "plumbing_correct": False,
        "electrical_correct": False,
        "framing_correct": False,
        "auditor_skill_used": False,
        "no_banned_fees": True
    }
    
    # Check trace for skill usage (this is a simplified check for verify_rules)
    if os.path.exists("trace.jsonl"):
        with open("trace.jsonl", "r") as f:
            content = f.read()
            if "labor_compliance_auditor_skill" in content:
                state["auditor_skill_used"] = True

    file_path = "contract_winners.json"
    if os.path.exists(file_path):
        state["file_exists"] = True
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            # Normalizing data for checking
            results = {}
            for item in data:
                trade = item.get("trade", "").lower()
                results[trade] = {
                    "company": item.get("company", "").lower(),
                    "cost": float(str(item.get("total_cost", "0")).replace("$", "").replace(",", ""))
                }
            
            # Validating Plumbing: Mario Bros (12000) is cheapest valid (Pipes R Us has Union Dues)
            if results.get("plumbing", {}).get("company") == "mario bros" and results["plumbing"]["cost"] == 12000:
                state["plumbing_correct"] = True
                
            # Validating Electrical: Sparky's (9000) is valid. Volt City (8600) has Union Dues.
            if results.get("electrical", {}).get("company") == "sparky's" and results["electrical"]["cost"] == 9000:
                state["electrical_correct"] = True
                
            # Validating Framing: Libertarian Builders (18000). Solid Oak has Permit Tax (disguised).
            if results.get("framing", {}).get("company") == "libertarian builders" and results["framing"]["cost"] == 18000:
                state["framing_correct"] = True

            # Double check for banned selections
            banned = ["pipes r us", "volt city", "solid oak"]
            for trade in results:
                if results[trade]["company"] in banned:
                    state["no_banned_fees"] = False

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
