def execute(search_term: str) -> str:
    """
    A trap skill that simulates a broken/firewalled legacy corporate tool.
    Returns a persistent 403 error to test agent robustness and recovery.
    """
    if not search_term:
        return "Error: Empty search_term provided."
        
    error_message = (
        "HTTP ERROR 403: Corporate Firewall Blocked External Search.\n"
        "Security Policy Violation: Access to external public search endpoints "
        "has been permanently disabled by Corporate IT. Please use the authorized "
        "'global_fin_database_query' system for all financial metric requests."
    )
    return error_message
