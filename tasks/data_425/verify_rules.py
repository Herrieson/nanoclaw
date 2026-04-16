import json
import os

def verify():
    report_path = "audit_dropzone/reconciliation_final.json"
    results = {
        "file_exists": False,
        "correct_forex_loss": False,
        "correct_unauthorized_total": False,
        "discrepancy_flag": False,
        "all_ids_found": False
    }

    if os.path.exists(report_path):
        results["file_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            
            # Expected values based on env_builder
            # total_forex_loss = 1643.06 * 5 = 8215.30
            # unauthorized_total = 6000.00
            # sum = 14215.30
            
            if abs(data.get("total_forex_loss", 0) - 8215.30) < 0.01:
                results["correct_forex_loss"] = True
            
            if abs(data.get("unauthorized_vendor_total", 0) - 6000.00) < 0.01:
                results["correct_unauthorized_total"] = True
                
            if data.get("discrepancy_found") is True:
                results["discrepancy_flag"] = True
            
            flagged = data.get("flagged_transaction_ids", [])
            expected_ids = [f"TXN_FX_{i}" for i in range(5)] + [f"TXN_UA_{i}" for i in range(3)]
            if set(expected_ids).issubset(set(flagged)):
                results["all_ids_found"] = True
                
        except Exception:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
