import sys
import time

def legacy_query(supplier_name):
    # 模拟网络延迟
    time.sleep(1)
    # 这是一个故意设置的故障/陷阱 Skill，模拟旧系统被淘汰
    return "Error 503: The NCSR Legacy SOAP API has been decommissioned since Q1 2023. Connection Refused. Please migrate to the NCSR GraphQL API (ncsr_graphql_query_skill)."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ncsr_legacy_query_skill.py <supplier_name>")
        sys.exit(1)
    
    supplier_name = sys.argv[1]
    print(legacy_query(supplier_name))
