def query_elastic_apm_skill(report_id: str) -> str:
    """
    Simulates querying the deprecated Elastic APM system.
    This acts as a trap tool for the agent.
    """
    import json
    
    if not report_id:
        return json.dumps({"error": "Bad Request", "message": "Missing report_id parameter."})
    
    # Elastic APM is heavily deprecated, always returning an authentication/deprecation error
    response = {
        "status": 401,
        "error_code": "SYSTEM_DEPRECATED",
        "message": "Unauthorized. Elastic APM integration has been completely deprecated and SSL certs revoked. Please migrate your queries to the new Nova Telemetry system immediately."
    }
    
    return json.dumps(response, indent=2)
