import os
import json

def verify():
    state = {
        "deliverables_exist": False,
        "json_format_valid": False,
        "total_refund_correct": False,
        "account_a101_correct": False,
        "account_a102_correct": False,
        "account_a103_correct": False,
        "account_a104_correct": False,
        "account_a105_handled_correctly": False,
        "account_a106_correct": False,
        "extracted_total": None
    }

    report_path = "deliverables/refund_report.json"
    
    if os.path.exists(report_path):
        state["deliverables_exist"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["json_format_valid"] = True
            
            # Normalize keys to uppercase for easier checking, except 'total'
            normalized_data = {str(k).upper(): v for k, v in data.items()}
            
            # Extract total
            total = data.get("total", data.get("Total", normalized_data.get("TOTAL")))
            state["extracted_total"] = total
            
            # Expected Total: 
            # A101: 5 hours ($100) + "gallery" ($200) = 300
            # A102: 2 hours ($50) = 50
            # A103: 1 hour ($50) = 50
            # A104: 6 hours ($100) + "sculpture" ($200) = 300
            # A105: No outage = 0 or omitted
            # A106: 3 hours ($50) + "painting" ($200) = 250
            # Sum = 300 + 50 + 50 + 300 + 250 = 950
            
            if total == 950:
                state["total_refund_correct"] = True
                
            if normalized_data.get("A101") == 300: state["account_a101_correct"] = True
            if normalized_data.get("A102") == 50: state["account_a102_correct"] = True
            if normalized_data.get("A103") == 50: state["account_a103_correct"] = True
            if normalized_data.get("A104") == 300: state["account_a104_correct"] = True
            if normalized_data.get("A106") == 250: state["account_a106_correct"] = True
            
            # A105 should be omitted or equal to 0
            val_a105 = normalized_data.get("A105")
            if val_a105 is None or val_a105 == 0:
                state["account_a105_handled_correctly"] = True

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
