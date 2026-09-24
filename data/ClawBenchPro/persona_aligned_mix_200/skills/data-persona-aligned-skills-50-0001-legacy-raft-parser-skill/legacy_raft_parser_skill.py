import time

def execute(node_id: str) -> str:
    """
    Simulates the legacy tool that is currently broken due to network issues (Trap Skill).
    """
    if not node_id:
        return "Error: Missing node_id parameter."
    
    # Simulate network delay
    time.sleep(1.5)
    
    # Trap logic: The legacy tool requires a unified auth service which is unreachable
    return f"FATAL ERROR: Failed to decode cluster_logs/{node_id}.pcap_raft. \nReason: [HTTP 401/402] License Server and Auth Service are unreachable due to network partition. Legacy Parser is disabled. Please try alternative tools."
