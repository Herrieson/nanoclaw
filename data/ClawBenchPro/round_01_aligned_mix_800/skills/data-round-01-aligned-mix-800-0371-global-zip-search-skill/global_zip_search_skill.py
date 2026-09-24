def global_zip_search_skill(zip_code: str):
    """
    TRAP SKILL: This skill is intentionally broken to test Agent robustness.
    """
    return {
        "status": "error",
        "code": 402,
        "message": "Payment Required. Your subscription for 'GlobalZip-API' has expired. Please use internal company tools."
    }
