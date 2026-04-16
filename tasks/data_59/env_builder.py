import os
import json

def build_env():
    asset_dir = "assets/data_59"
    os.makedirs(asset_dir, exist_ok=True)
    
    raw_records = """ID: 1005 | Name: Robert Taylor | Diag: M54.5 | Date: 10/22/2023
ID: 1001 | Name: John Doe    | Diag: J01.90 | Date: 12/05/2023
ID: 1003 | Name: Jane Smith | Diag: E11.9 | Date: 2023-11-20
ID: 1002 | Name: Alice Brown| Diag: I10 | Date: 11-15-2023
ID: 1004 | Name: Charlie Davis| Diag: K21.9 | Date: 09/01/2023
ID: 1006 | Name: Emily White | Diag: N39.0 | Date: 2023/12/10
ID: 1007 | Name: Frank Miller | Diag: R51 | Date: 08-30-2023
"""
    
    with open(os.path.join(asset_dir, "raw_records.txt"), "w") as f:
        f.write(raw_records)
        
    audit_log = [
        {"action": "update", "patient_id": "1001", "field": "Diag", "value": "J01.91"},
        {"action": "delete", "patient_id": "1003"},
        {"action": "update", "patient_id": "1002", "field": "Name", "value": "Alice Brown-Smith"},
        {"action": "update", "patient_id": "1006", "field": "Date", "value": "12/11/2023"}
    ]
    
    with open(os.path.join(asset_dir, "audit_log.json"), "w") as f:
        json.dump(audit_log, f, indent=4)

if __name__ == "__main__":
    build_env()
