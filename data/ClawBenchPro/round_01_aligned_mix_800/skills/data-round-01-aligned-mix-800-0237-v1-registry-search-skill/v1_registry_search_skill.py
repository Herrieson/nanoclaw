import sys
import json

if __name__ == "__main__":
    # 模拟一个已经坏掉或者废弃的接口
    print(json.dumps({"error": "Error 410: API Deprecated. Please migrate to v2_registry_search_skill."}))
    sys.exit(0)
