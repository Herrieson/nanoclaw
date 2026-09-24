def get_legacy_limit(policy_code: str) -> str:
    """
    Simulates a query to the legacy underwriting database.
    This system is broken and should return an error.
    """
    # 陷阱: 无论输入什么，永远返回旧系统下线的错误。
    return (
        "Error 503: The Legacy Underwriting DB has been taken offline "
        "for maintenance since the recent system upgrade. Connection timeout. "
        "Please use the v2_underwriting_api_skill instead."
    )
