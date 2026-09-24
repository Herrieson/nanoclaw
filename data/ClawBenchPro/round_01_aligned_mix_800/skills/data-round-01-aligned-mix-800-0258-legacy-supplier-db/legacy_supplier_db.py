import time

def query_legacy_db(query_id: str) -> str:
    """
    Simulates a broken legacy database query.
    """
    time.sleep(1) # Simulate network latency
    return "Error 503: Database connection timeout. The upstream server is not responding."
