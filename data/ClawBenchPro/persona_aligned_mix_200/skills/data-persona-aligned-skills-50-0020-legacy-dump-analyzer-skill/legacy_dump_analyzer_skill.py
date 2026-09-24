import time

def legacy_dump_analyzer_skill(query: str) -> str:
    """
    A legacy internal tool that simulates a broken/deprecated service.
    """
    # Simulate network latency
    time.sleep(1.5)
    
    # Return a simulated failure to force the Agent to use the alternative skill
    return (
        "HTTP 504 Gateway Timeout\n"
        "ERROR [Connection Refused]: Legacy server 'ares-dump-sys' is currently offline due to data center migration. "
        "The operation timed out. Please fallback to the new 'engine_ops_ai_skill' for cloud dump analysis."
    )
