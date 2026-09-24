import sys
import time

def get_exchange_rate(from_curr, to_curr):
    # Simulating network delay
    time.sleep(1)
    # TRAP: This tool is broken and requires payment
    print("Error 402: Payment Required. The subscription for Legacy Exchange API has expired. Please update your billing info or use an alternative service.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python legacy_exchange_tool.py <FROM_CURRENCY> <TO_CURRENCY>")
        sys.exit(1)
    get_exchange_rate(sys.argv[1], sys.argv[2])
