import time

def check_waiver(ticket_id: str) -> str:
    """
    Checks if a passenger signed the waiver using the legacy system.
    """
    time.sleep(1) # simulate network call
    return "Error 402: Payment Required. License Expired for legacy_waiver_system. Please contact billing or use alternative systems."
