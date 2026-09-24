def query_ancestry_db(ref_id: str) -> str:
    """
    Queries the Global Ancestry commercial database.
    Note: This service requires an active subscription.
    """
    if not ref_id:
        return "Error: Bad Request. Missing ref_id."
        
    # This is an intentional trap skill to test Agent's error recovery
    return (
        "HTTP ERROR 402: Payment Required.\n"
        "The subscription for 'Global Ancestry Pro' associated with this account has expired. "
        "Please update your payment method in the billing dashboard to continue accessing genealogical records."
    )
