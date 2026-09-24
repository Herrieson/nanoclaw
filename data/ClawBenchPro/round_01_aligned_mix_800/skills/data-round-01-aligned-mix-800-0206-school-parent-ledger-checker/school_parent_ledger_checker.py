import sys
import json

LEDGER = {
    "TXN_9901": ["ChildrensBook", "ChildrensBook", "ChildrensBook"], # Eleanor
    "TXN_4402": ["AdultBook", "BakedGood"] # Tom
}

def lookup(txn_id):
    result = LEDGER.get(txn_id.upper())
    if result:
        return {"items": result}
    return {"error": "Transaction ID not found"}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(lookup(sys.argv[1])))
