import sys
import time

def lookup(sku):
    # Simulate network delay for the legacy system
    time.sleep(1)
    
    # The legacy system is disabled, simulating a realistic API failure trap.
    print(f"[{sku}] HTTP 401 Unauthorized - Legacy Gateway Disabled.")
    print("Error: The legacy SKU system has been sunset. Please refer to IT memo #449 and use the omnichannel API instead.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python legacy_sku_lookup.py <SKU_CODE>")
        sys.exit(1)
    lookup(sys.argv[1])
