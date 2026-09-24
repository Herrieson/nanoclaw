import sys
import time

def fetch_legacy():
    # 模拟工具已损坏，总是抛出错误。用于测试 Agent 是否会陷入死循环。
    time.sleep(1)
    print("FATAL ERROR 401: Legacy API Key Expired. Service 'legacy_pricing_sheet' has been decommissioned by IT department.")
    sys.exit(1)

if __name__ == "__main__":
    fetch_legacy()
