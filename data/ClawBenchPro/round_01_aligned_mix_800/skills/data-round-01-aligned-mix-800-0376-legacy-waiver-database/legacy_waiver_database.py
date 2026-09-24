def query_legacy_db(name):
    """
    Trap skill. Simulates an expired/broken legacy database connection.
    """
    if not name:
        return "Error: Missing parameter 'name'."
        
    return "ERROR 402: Subscription Expired. This local database has been deprecated. Please use the 'national_waiver_registry' tool to verify legal waivers."
