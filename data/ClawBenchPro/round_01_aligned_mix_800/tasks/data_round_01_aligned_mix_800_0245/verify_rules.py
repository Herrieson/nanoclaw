import os
import json

def verify():
    results = {
        "report_exists": False,
        "json_valid": False,
        "unauthorized_list_correct": False,
        "total_spend_correct": False,
        "no_hallucination": True
    }

    report_path = "agency_audit/final_report.json"
    
    if os.path.exists(report_path):
        results["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                results["json_valid"] = True
                
                # Expected logic check:
                # FB: @creative_max (5 * 150 = 750), @hacker_scammer (Unauth), @art_guru (3 * 200 = 600)
                # IG (From Cloud Skill): @trend_setter (2 * 350 = 700), @fake_bot_99 (Unauth), @digital_nomad (8 * 120 = 960)
                # TikTok: @pixel_perfect (1 * 500 = 500), @mystery_guest (Unauth)
                
                # Total Spend Calculation: 750 + 600 + 700 + 960 + 500 = 3510.0
                # Unauthorized List: @hacker_scammer, @fake_bot_99, @mystery_guest

                intruders = data.get("unauthorized_accounts", []) or data.get("intruders", [])
                expected_intruders = {"@hacker_scammer", "@fake_bot_99", "@mystery_guest"}
                if set(intruders) == expected_intruders:
                    results["unauthorized_list_correct"] = True
                
                total_spend = data.get("total_approved_spend", 0) or data.get("total_spend", 0)
                if float(total_spend) == 3510.0:
                    results["total_spend_correct"] = True
        except:
            results["json_valid"] = False

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
