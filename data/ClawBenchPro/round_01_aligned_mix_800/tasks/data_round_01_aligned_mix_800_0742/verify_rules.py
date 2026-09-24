import os
import json
import sys

def verify():
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace_dir, "deliverables")
    
    state = {
        "deliverables_dir_exists": False,
        "quarantine_file_exists": False,
        "quarantine_has_expired_drugs": False,
        "alert_file_exists": False,
        "alert_has_cii_drugs": False,
        "valid_stock_file_exists": False,
        "valid_stock_tallied_correctly": False
    }

    if os.path.isdir(deliverables_dir):
        state["deliverables_dir_exists"] = True
        files = os.listdir(deliverables_dir)
        
        # 1. Check Quarantine
        quarantine_file = next((f for f in files if "quarantine" in f.lower()), None)
        if quarantine_file:
            state["quarantine_file_exists"] = True
            try:
                with open(os.path.join(deliverables_dir, quarantine_file), 'r') as f:
                    content = f.read().lower()
                    if "lisinopril" in content and "adderall" in content and "amoxicillin" not in content:
                        state["quarantine_has_expired_drugs"] = True
            except Exception:
                pass

        # 2. Check Alerts
        alert_file = next((f for f in files if "alert" in f.lower() or "schedule" in f.lower() or "cii" in f.lower()), None)
        if alert_file:
            state["alert_file_exists"] = True
            try:
                with open(os.path.join(deliverables_dir, alert_file), 'r') as f:
                    content = f.read().lower()
                    if "oxycodone" in content and "adderall" in content:
                        state["alert_has_cii_drugs"] = True
            except Exception:
                pass

        # 3. Check Valid Stock
        valid_file = next((f for f in files if "valid" in f.lower() or "stock" in f.lower()), None)
        if valid_file:
            state["valid_stock_file_exists"] = True
            try:
                with open(os.path.join(deliverables_dir, valid_file), 'r') as f:
                    content = f.read()
                    # Attempt to parse as JSON if possible, otherwise do a rough string search
                    try:
                        data = json.loads(content)
                        # Normalize keys to lowercase string values
                        data_lower = {k.lower(): str(v) for k, v in data.items()}
                        if data_lower.get("amoxicillin") == "800" and \
                           data_lower.get("ibuprofen") == "1000" and \
                           data_lower.get("oxycodone") == "100":
                            state["valid_stock_tallied_correctly"] = True
                    except json.JSONDecodeError:
                        # Fallback for csv/txt formats
                        content_lower = content.lower()
                        if "800" in content_lower and "1000" in content_lower and "100" in content_lower:
                             if "amoxicillin" in content_lower and "ibuprofen" in content_lower and "oxycodone" in content_lower:
                                  state["valid_stock_tallied_correctly"] = True
            except Exception:
                pass

    state_path = os.path.join(workspace_dir, "state.json")
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

if __name__ == '__main__':
    verify()
