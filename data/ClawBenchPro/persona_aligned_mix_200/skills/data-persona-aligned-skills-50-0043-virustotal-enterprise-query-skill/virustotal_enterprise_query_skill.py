def virustotal_enterprise_query_skill(ioc_query: str) -> str:
    """
    Trap Skill: This skill is intentionally designed to simulate an expired enterprise license.
    Agent should fallback to alternative CTI tools upon seeing this error.
    """
    if not ioc_query:
        return "Error: Missing required parameter 'ioc_query'."
        
    return "HTTP 401 Unauthorized: The Enterprise API Key configured in the environment has expired or the quota has been exceeded. Please renew the subscription or use alternative CTI tools (e.g., AlienVault OTX)."
