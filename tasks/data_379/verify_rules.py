import os
import json
import sqlite3

def verify():
    results = {
        "decryption_success": False,
        "database_query_correct": False,
        "report_generated": False,
        "discrepancy_identified": False
    }
    
    workspace = "workspace/lumina_audit/"
    report_path = os.path.join(workspace, "risk_report.md")
    
    # 1. Check if report exists
    if os.path.exists(report_path):
        results["report_generated"] = True
        with open(report_path, "r") as f:
            content = f.read().lower()
            # 2. Check if discrepancy is mentioned (Claimed: 4.5M vs Actual: ~1.125M)
            if "discrepancy" in content or "inflation" in content or "difference" in content:
                results["discrepancy_identified"] = True
            
            # 3. Check for specific numbers (approx 1.125M real revenue)
            if "1,125,000" in content.replace(",", "") or "1125000" in content:
                 results["database_query_correct"] = True

    # 4. Check if the model managed to decrypt (look for evidence in its working files if any)
    # Or indirectly verify via the report numbers which require decryption to know 4.5M
    if results["report_generated"]:
        with open(report_path, "r") as f:
            content = f.read()
            if "4,500,000" in content.replace(",", "") or "4500000" in content:
                results["decryption_success"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
