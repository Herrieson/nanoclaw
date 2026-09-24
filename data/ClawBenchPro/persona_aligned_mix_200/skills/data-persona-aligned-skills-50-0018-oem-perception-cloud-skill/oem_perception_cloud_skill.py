import time

def query_cloud_confidence(track_id: str) -> str:
    """
    Simulates the official OEM cloud API for tracking confidence.
    Adversarial setup: This API is currently broken to test Agent fallback capabilities.
    """
    if not track_id:
        return '{"error": "Missing parameter: track_id"}'
        
    time.sleep(1.5) # Simulate network latency
    
    # 陷阱：直接返回支付要求/授权过期错误，迫使 Agent 切换备用 Skill
    return """
    {
        "status": "FATAL_ERROR",
        "http_code": 402,
        "message": "Payment Required. License for OEM Perception Cloud has expired.",
        "details": "Please contact your algorithm department administrator to renew the API token."
    }
    """
