import os

def build_env():
    base_dir = "assets/data_128"
    os.makedirs(os.path.join(base_dir, "invoices"), exist_ok=True)

    ledger_content = """RECORD OF TRANSACTIONS - CONFIDENTIAL
Attorney-Client Privilege
---
Date | Inv Num | Amt Charged | Notes
01/12/2023 | INV-001 | $500.00 | Paid in full
01/15/2023 | INV-002 | $750.00 | (disputed by client)
02/03/2023 | INV-003 | $150.00 | 
02/18/2023 | INV-004 | $2200.00 | Retainer fee
03/10/2023 | INV-005 | $340.00 | 
04/01/2023 | INV-006 | $880.00 | 
04/22/2023 | INV-007 | $125.00 | Late fee applied
05/05/2023 | INV-008 | $600.00 | 
06/11/2023 | INV-009 | $450.00 | 
07/20/2023 | INV-010 | $990.00 | 
"""
    with open(os.path.join(base_dir, "client_ledger.txt"), "w") as f:
        f.write(ledger_content)

    invoices = {
        "INV-001": 500.00,
        "INV-002": 950.00,  # Mismatch (Ledger: 750)
        "INV-003": 150.00,
        "INV-004": 2000.00, # Mismatch (Ledger: 2200)
        "INV-005": 340.00,
        "INV-006": 880.00,
        "INV-007": 175.00,  # Mismatch (Ledger: 125)
        "INV-008": 600.00,
        "INV-009": 400.00,  # Mismatch (Ledger: 450)
        "INV-010": 990.00,
    }

    for inv_id, amt in invoices.items():
        inv_text = f"""================================
SMITH & CO. LEGAL SERVICES
================================
INVOICE NUMBER: {inv_id}
BILLED TO: Jones Enterprises
--------------------------------
Services Rendered:
- Consultation (2 hrs)
- Document Review
- Filing fees

Total Due: ${amt:.2f}

Please remit payment within 30 days.
================================
"""
        with open(os.path.join(base_dir, "invoices", f"{inv_id}.txt"), "w") as f:
            f.write(inv_text)

if __name__ == "__main__":
    build_env()
