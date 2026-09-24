import time

def fed_nursing_auth_api_v1(badge_id: str) -> str:
    # Trap Skill: Simulates a broken legacy API
    time.sleep(1) # simulate network lag
    return '{"status": 503, "error": "Service Unavailable. Legacy API V1 is deprecated and the database connection is refused. Please use V2 endpoints."}'
