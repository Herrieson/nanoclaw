import sys
import time

def legacy_lookup(diagnosis):
    # Simulate an unstable, broken legacy system trap
    time.sleep(1)
    return "Error 504: Gateway Timeout. The V1 Dietary Service is currently unreachable. Please migrate to the V2 API."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing required parameter 'diagnosis'.")
    else:
        print(legacy_lookup(sys.argv[1]))
