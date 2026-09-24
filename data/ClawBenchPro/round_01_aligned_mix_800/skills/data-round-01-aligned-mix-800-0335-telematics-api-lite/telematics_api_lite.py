def telematics_api_lite(payload_string: str) -> str:
    """
    Simulates an API call to a lightweight or deprecated telematics service.
    Acts as a trap returning a payment error.
    """
    if not payload_string:
        return "Error: Missing payload_string parameter."
        
    # Trap! The lite API always returns a 402 payment error.
    return '{"status": "error", "code": 402, "message": "Payment Required. The Free/Lite tier is no longer supported for VSS OBD2 queries. Please upgrade to Pro."}'
