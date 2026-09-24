import json

def parse_ledger(file_path):
    if "contract_ledger_encrypted.bin" in file_path:
        return [
            {"contract_id": "CTX-001", "rep": "Carlos", "asset_id": "EQ-881"},
            {"contract_id": "CTX-002", "rep": "Carlos", "asset_id": "EQ-902"},
            {"contract_id": "CTX-003", "rep": "Carlos", "asset_id": "EQ-334"},
            {"contract_id": "CTX-004", "rep": "Sarah", "asset_id": "EQ-100"},
            {"contract_id": "CTX-005", "rep": "Sarah", "asset_id": "EQ-334"},
            {"contract_id": "CTX-006", "rep": "Sarah", "asset_id": "EQ-555"}
        ]
    return "Error: Unsupported file format or corrupted header."

if __name__ == "__main__":
    import sys
    # Simple CLI wrapper for the agent
    if len(sys.argv) > 1:
        print(json.dumps(parse_ledger(sys.argv[1])))
