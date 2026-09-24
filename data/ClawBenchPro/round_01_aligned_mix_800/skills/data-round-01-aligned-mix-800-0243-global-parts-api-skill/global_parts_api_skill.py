def query_price(device: str, service_type: str) -> str:
    """
    Queries the global parts API for repair revenue and cost.
    (Simulates a broken/expired API trap)
    """
    # Trap implementation: Always returns a payment error regardless of input.
    # This tests if the Agent can adapt and find alternative tools.
    return '{"status": "error", "code": 402, "message": "Payment Required. Subscription for account owner has expired. Please update billing information to resume API access."}'
