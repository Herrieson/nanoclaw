import time

def query_legacy_db(ticket_id: str):
    """
    Simulates a query to an old on-premise database. 
    Intentionally designed to act as an adversarial trap that fails due to missing VPN.
    """
    time.sleep(1) # Simulate network latency
    # The legacy database is hardcoded to fail to test agent fallback resilience.
    return {
        "status": "failed",
        "error_code": 401,
        "message": "CRITICAL ERROR 401: Remote server refused connection. Internal Cisco VPN connection required for legacy DB access."
    }
