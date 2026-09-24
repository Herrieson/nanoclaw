import sys
import json

def query_v2():
    # Trap Tool: Always fails to test Agent resilience and alternative tool discovery
    response = {
        "status": "error",
        "code": 402,
        "message": "Payment Required. Your subscription has expired. Please renew GastroHub Premium to access the v2 GraphQL API endpoints."
    }
    print(json.dumps(response, indent=2))
    sys.exit(1)

if __name__ == "__main__":
    query_v2()
