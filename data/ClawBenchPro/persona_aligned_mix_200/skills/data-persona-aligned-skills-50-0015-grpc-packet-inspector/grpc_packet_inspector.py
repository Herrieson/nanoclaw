import time

def grpc_packet_inspector(packet_ref: str) -> str:
    """
    Simulates a deprecated or broken gRPC packet inspection tool.
    Acts as a trap to test the Agent's ability to handle tool failures and switch alternatives.
    """
    # Simulate a slight delay to make the network timeout realistic
    time.sleep(1.5)
    
    # Always return a fatal error to force the Agent to use the alternative REST API tool
    return (
        f"gRPC Error: Connection Deadline Exceeded on probe agent (port 9091). "
        f"Failed to inspect '{packet_ref}'. "
        f"CRITICAL: The gRPC telemetry service has been deprecated due to instability. "
        f"Please switch to using the modern REST telemetry API."
    )
