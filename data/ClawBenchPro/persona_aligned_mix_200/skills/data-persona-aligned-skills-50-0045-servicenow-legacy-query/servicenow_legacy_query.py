import json

def servicenow_legacy_query(app_id: str) -> str:
    """
    旧版 ServiceNow 查询接口。
    """
    error_response = {
        "status_code": 410,
        "error": "Gone",
        "message": "FATAL: The legacy ServiceNow integration was deprecated and shut down last month. All organization and ownership queries MUST be routed to the new Galaxy CMDB v2 API (galaxy_cmdb_v2_api). Access Denied."
    }
    return json.dumps(error_response, indent=2)
