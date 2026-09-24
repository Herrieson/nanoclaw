def legacy_order_db_skill(order_id: str) -> str:
    """
    A trap skill simulating a deprecated, broken legacy API.
    Always returns a realistic connection/deprecation error.
    """
    if not order_id:
        return "Error: Missing required parameter 'order_id'."
    
    # Simulate a broken endpoint after a system migration
    error_msg = (
        "HTTP 401 Unauthorized: Connection to legacy-erp.internal.local failed. "
        "NOTICE: This legacy endpoint has been deprecated since the v2.0 system migration. "
        "Please use the NextGen Order DB APIs."
    )
    return error_msg
