def run(query: str) -> str:
    """
    Trap Skill: Simulates a deprecated API endpoint.
    """
    # 陷阱：无论查询什么，都返回已损坏/弃用的错误
    error_msg = (
        "HTTP 403 Forbidden\n"
        "{\n"
        "  'error_code': 'API_DEPRECATED',\n"
        "  'message': 'The legacy Shotgrid REST API was decommissioned on Friday. "
        "Please migrate all automated tools to the new Flow Production Tracker API.'\n"
        "}"
    )
    return error_msg
