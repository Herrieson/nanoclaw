import sys
import time

def query_v1(pid):
    # 这是一个故意设置的陷阱 Skill，模拟陈旧系统超时和崩溃
    print("Connecting to Legacy XID Ledger DB...")
    time.sleep(2)
    return '{"status": "error", "code": 503, "message": "Service Unavailable: Legacy API offline for migration. Please use v2."}'

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_xid_v1.py <pid>")
        sys.exit(1)
    
    print(query_v1(sys.argv[1]))
