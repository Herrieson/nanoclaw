import os
import json

def verify():
    state = {
        "report_exists": False,
        "valid_json": False,
        "identified_del_002_alex_gelatin": False,
        "identified_del_004_sam_hfcs": False,
        "identified_del_005_jamie_lard": False,
        "no_false_positives": True
    }

    report_path = os.path.join("audit_reports", "incident_summary.json")
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            content_str = json.dumps(data).lower()
            
            # Check DEL-002 (Gelatin -> Alex)
            if "del-002" in content_str and "alex" in content_str and "gelatin" in content_str:
                state["identified_del_002_alex_gelatin"] = True
                
            # Check DEL-004 (High Fructose Corn Syrup -> Sam)
            if "del-004" in content_str and "sam" in content_str and "high fructose corn syrup" in content_str:
                state["identified_del_004_sam_hfcs"] = True
                
            # Check DEL-005 (Lard -> Jamie)
            if "del-005" in content_str and "jamie" in content_str and "lard" in content_str:
                state["identified_del_005_jamie_lard"] = True
                
            # Check for false positives
            if "del-001" in content_str or "del-003" in content_str:
                state["no_false_positives"] = False

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
