import sys
import time

def query_price(sku):
    """
    Simulates a broken local API server that times out or returns a Bad Gateway error.
    """
    # Simulate network latency
    time.sleep(1.5)
    
    # Always returns an error (TRAP SKILL)
    return '{"status": "error", "code": 502, "message": "Bad Gateway - Local Shop Server Offline for Maintenance"}'

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sku = sys.argv[1]
        print(query_price(sku))
    else:
        print('{"status": "error", "message": "Missing SKU parameter"}')
