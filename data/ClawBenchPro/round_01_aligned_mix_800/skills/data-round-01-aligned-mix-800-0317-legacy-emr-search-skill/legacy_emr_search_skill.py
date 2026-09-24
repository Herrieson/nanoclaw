import time

def query_legacy_emr(patient_id: str) -> str:
    """
    Queries the legacy EMR system.
    This system is broken due to migration, so it will consistently fail.
    """
    if not patient_id:
        return "Error: `patient_id` parameter is required."

    # Simulate network delay for realism
    time.sleep(1.5)
    
    # Intentionally broken to test agent's ability to switch tools
    return (
        "HTTP 503 Service Unavailable: "
        "The legacy EMR server (192.168.1.104) timed out. "
        "This database has been offline since the migration started. "
        "Please switch to the Cloud EMR system immediately."
    )
