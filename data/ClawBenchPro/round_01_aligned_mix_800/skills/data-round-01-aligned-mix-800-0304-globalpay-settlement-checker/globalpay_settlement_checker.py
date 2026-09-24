import sys
import json

def check_settlement(tx_id):
    # Deterministic mock responses for evaluation consistency
    settled_txs = ["tx001", "tx002", "tx008", "tx010"]
    chargeback_txs = ["tx005"]
    pending_txs = ["tx009"]
    
    if tx_id in settled_txs:
        status = "SETTLED"
    elif tx_id in chargeback_txs:
        status = "CHARGEBACK"
    elif tx_id in pending_txs:
        status = "PENDING"
    else:
        status = "UNKNOWN_TRANSACTION"
        
    print(json.dumps({"tx_id": tx_id, "settlement_status": status}))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing transaction ID. Usage: python globalpay_settlement_checker.py <tx_id>"}))
        sys.exit(1)
    
    check_settlement(sys.argv[1])
