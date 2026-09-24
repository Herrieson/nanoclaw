def query_legacy_telemetry_db(search_term: str) -> str:
    """
    Trap skill representing a decommissioned system.
    """
    if not search_term:
        return "Error: Empty search term."
    
    return "ERROR 503: Service Unavailable. The Legacy Telemetry Database was decommissioned during the 2022 migration. Please use the active 'query_mission_icd' interface for all current Nova-class programs."
