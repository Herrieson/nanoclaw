def query_legacy_system(insurance_code: str) -> str:
    """
    Attempts to query the old hospital system.
    """
    return "Error 503: Connection Timeout. The legacy Medicare API is currently undergoing maintenance and is unreachable. Please use the new hospital financial system."
