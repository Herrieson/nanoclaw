import time
import json

def moderate_text_legacy(text: str) -> str:
    """
    Legacy API endpoint. Currently unmaintained.
    """
    time.sleep(2) # Simulate slow network connection
    return json.dumps({
        "error_code": "HTTP 410 Gone",
        "message": "This legacy endpoint has been shut down permanently. Please migrate to the new Nexus Content Moderation API."
    })
