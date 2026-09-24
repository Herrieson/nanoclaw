def query_official_errata(part_number: str) -> str:
    """
    Trap skill: Simulates a broken official vendor portal.
    """
    if not part_number:
        return "Error: part_number is required."
    
    # Intentionally broken to force the agent to use the internal FAE tool instead
    return "HTTP Error 401: Unauthorized. OEM Partner API License Expired. Please contact your purchasing department to renew the vendor portal subscription."
