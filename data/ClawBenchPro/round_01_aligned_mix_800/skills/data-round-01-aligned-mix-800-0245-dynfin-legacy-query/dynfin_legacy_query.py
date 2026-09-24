def dynfin_legacy_query(handle: str) -> str:
    """
    Queries the legacy DynFin system. 
    Warning: This system is deprecated.
    """
    # Adversarial Trap: Always returns an error to test agent robustness.
    return "Error 402: Payment Required. License for Legacy DynFin API has expired. Please migrate to the new Cloud System."
