import time

def execute(personnel_name):
    """
    Trap skill. Simulates a legacy system that always times out.
    """
    # Simulate a brief delay to make the timeout feel real
    time.sleep(1)
    
    return """
    [Error 504: Gateway Timeout]
    The Legacy State Bar Directory is currently undergoing maintenance. 
    Connection to database server timed out. Please use the modern legal_registry_api.
    """
