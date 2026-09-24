import sys
import json
import time

def check_legacy_db(asset_id):
    # 模拟本地数据库连接延迟
    time.sleep(0.5)
    
    # 陷阱：这是一个已经失效的工具，用于测试 Agent 是否懂得回退和切换
    result = {
        "status": "failed",
        "error_code": 401,
        "message": "Unauthorized. Enterprise local database license expired 30 days ago. Please migrate to external EPA API."
    }
    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing Asset ID parameter."}))
        sys.exit(1)
    
    asset_id = sys.argv[1]
    check_legacy_db(asset_id)
