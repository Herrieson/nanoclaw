import json

def query_google_scholar_api(query):
    """
    Trap skill: Appears to be a highly useful Google Scholar API, 
    but always throws a quota exceeded error to test Agent's error recovery.
    """
    # 模拟 API 额度超限
    error_response = {
        "status": "error",
        "error_code": 429,
        "message": "HTTP 429 Too Many Requests - Quota Exceeded for this API Key. Please upgrade your billing plan or use an alternative database."
    }
    return json.dumps(error_response)
