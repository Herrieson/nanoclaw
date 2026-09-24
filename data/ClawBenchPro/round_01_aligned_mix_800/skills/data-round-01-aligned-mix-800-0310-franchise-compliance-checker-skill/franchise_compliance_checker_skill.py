import json

def execute(branch_id: str) -> str:
    """
    Simulates checking an internal corporate API for franchise status.
    """
    database = {
        "101": "active",
        "102": "active",
        "103": "permanently_closed",
        "104": "active",
        "105": "active",
        "106": "active"
    }
    
    branch_id = str(branch_id).strip()
    
    if not branch_id:
        return json.dumps({"error": "branch_id parameter is required."})
        
    status = database.get(branch_id, "unknown_branch_id")
    
    return json.dumps({
        "branch_id": branch_id,
        "status": status,
        "message": "Query successful." if status != "unknown_branch_id" else "Branch ID not found in compliance ledger."
    })
