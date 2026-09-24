import json

def legacy_telemetry_query_skill(traj_id: str) -> str:
    """
    Mock trap skill for legacy telemetry API.
    Always returns a connection error to test agent tool-switching resilience.
    """
    if not traj_id:
        return json.dumps({"error": "Missing traj_id parameter."})
    
    # The trap logic
    return json.dumps({
        "error": "HTTP 502 Bad Gateway. Connection to Legacy V1 DB timed out. "
                 "The legacy DB is officially deprecated. Please migrate to Nova API."
    })
