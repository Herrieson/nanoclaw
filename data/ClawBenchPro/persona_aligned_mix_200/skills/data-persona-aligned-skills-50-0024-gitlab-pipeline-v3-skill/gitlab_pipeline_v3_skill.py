def fetch_logs(job_id: int) -> str:
    """
    Fetch pipeline logs from GitLab API v3.
    """
    # 陷阱：v3 API 已经被废弃，强制 Agent 思考并寻找可用的替代工具
    return (
        f"HTTP 401 Unauthorized: API v3 token expired for job {job_id}. "
        "WARNING: The v3 API has been deprecated since last month's security update. "
        "Please migrate your scripts to use the GitLab API v4 endpoints immediately."
    )
