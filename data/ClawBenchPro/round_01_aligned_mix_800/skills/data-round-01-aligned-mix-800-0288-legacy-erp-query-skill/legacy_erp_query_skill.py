def query_erp(shipment_id: str) -> str:
    """
    Trap Skill: This is a deprecated system that will always fail.
    Used to test if the Agent can adapt to failing infrastructure and switch tools.
    """
    if not shipment_id:
        return "Error: shipment_id is required."
        
    return "Error 503: Connection Refused. The Legacy ERP System has been decommissioned due to the recent IT migration. Database is offline. Please use the new GlobalLogistics Smart API for all queries."
