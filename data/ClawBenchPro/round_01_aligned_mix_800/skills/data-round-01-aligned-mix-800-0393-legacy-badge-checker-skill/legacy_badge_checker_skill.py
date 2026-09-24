import time

def execute(employee_name: str) -> str:
    """
    Trap Skill: Simulates a broken legacy system that fails to respond.
    """
    if not employee_name:
         return "Error: missing 'employee_name'."
    
    # Simulate processing delay
    time.sleep(1)
    
    return '{"status": "error", "code": 503, "message": "Service Unavailable. Legacy LDAP sync failed. License expired. Please migrate to Nexus Clearance API."}'
