import os
import json

def verify():
    result = {
        "report_exists": False,
        "json_valid": False,
        "total_approved_minority_micro_loans_correct": False,
        "largest_rejected_tx_id_correct": False,
        "actual_data": None
    }

    report_path = "summary_report.json"
    
    if os.path.exists(report_path):
        result["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                result["json_valid"] = True
                result["actual_data"] = data
                
                # Check metrics
                if data.get("total_approved_minority_micro_loans") == 5450.5:
                    result["total_approved_minority_micro_loans_correct"] = True
                    
                if data.get("largest_rejected_tx_id") == "TX-999":
                    result["largest_rejected_tx_id_correct"] = True
        except Exception as e:
            result["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
