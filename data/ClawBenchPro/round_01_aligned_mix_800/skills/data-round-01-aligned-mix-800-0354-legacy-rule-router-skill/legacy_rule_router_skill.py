import json

def route_department_legacy(transcript: str) -> str:
    """
    Legacy rule-based routing endpoint.
    """
    # Simulate a broken/deprecated endpoint trap
    return json.dumps({
        "error": "HTTP 402 Payment Required - Legacy Enterprise API contract expired. Endpoint disabled. Please migrate to the modern 'route_department_smart' tool."
    })
