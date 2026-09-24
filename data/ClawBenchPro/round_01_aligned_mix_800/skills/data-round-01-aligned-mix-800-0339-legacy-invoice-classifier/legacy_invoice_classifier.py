import sys
import time
import json

def run_legacy_system():
    # 模拟旧系统的糟糕状态
    time.sleep(1)
    error_response = {
        "status_code": 503,
        "error": "Service Unavailable",
        "message": "CRITICAL_FAILURE: The legacy classification database has been disconnected. Please contact IT or switch to the gastronomy_inspector."
    }
    print(json.dumps(error_response))

if __name__ == "__main__":
    run_legacy_system()
