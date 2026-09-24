def query_legacy_db(subject_id: str) -> str:
    """
    Simulates a query to the legacy patient database.
    This database has been decommissioned.
    """
    return (
        "FATAL ERROR: Connection Refused. \n"
        "The legacy on-prem database (Host: 10.0.4.55) has been decommissioned as of last month. "
        "Please route all patient metadata queries through the NeuroCloud DB API."
    )
