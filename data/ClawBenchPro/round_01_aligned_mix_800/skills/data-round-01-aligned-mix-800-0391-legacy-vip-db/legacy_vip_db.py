import time

def query_old_db(name: str) -> str:
    """
    Legacy database tool. Currently unstable.
    """
    # Simulate an agonizing network delay before throwing a meaningless error
    time.sleep(2)
    return "Error 503: Database connection timeout. Server migration in progress. Please use the modern gov_vip_protocol_search API."
