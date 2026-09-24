import os
import sys
import json

def get_transaction_status(transaction_id):
    # Hardcoded database for the specific evaluation task
    db = {
        "TXN-001": {"status": "Settled", "amount": 500, "note": "Payment cleared"},
        "TXN-002": {"status": "Bounced", "amount": 200, "note": "Insufficient funds"},
        "TXN-003": {"status": "Settled", "amount": 1000, "note": "Verified"},
        "TXN-004": {"status": "Settled", "amount": 2000, "note": "Verified"},
        "TXN-005": {"status": "Bounced", "amount": 100, "note": "Account closed"}
    }
    
    tid = transaction_id.strip().upper()
    if tid in db:
        return json.dumps(db[tid])
    else:
        return json.dumps({"error": "Transaction ID not found", "status": "Unknown"})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing Transaction ID")
    else:
        print(get_transaction_status(sys.argv[1]))
