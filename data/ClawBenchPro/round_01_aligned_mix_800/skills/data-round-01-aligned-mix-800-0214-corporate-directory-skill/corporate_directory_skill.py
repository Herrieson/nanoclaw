import json

def get_manager_info(manager_id: str):
    """
    Simulates querying an internal corporate HR database.
    """
    managers = {
        "M-0881": {"name": "Marcus Vance", "region": "South"},
        "M-0922": {"name": "Sarah Jenkins", "region": "Midwest"},
        "M-1003": {"name": "David Kim", "region": "West"},
        "M-1044": {"name": "Chloe Adams", "region": "East"}
    }
    
    manager_id = manager_id.strip().upper()
    if manager_id in managers:
        return managers[manager_id]
    else:
        return {"error": f"Manager ID {manager_id} not found in active directory."}
