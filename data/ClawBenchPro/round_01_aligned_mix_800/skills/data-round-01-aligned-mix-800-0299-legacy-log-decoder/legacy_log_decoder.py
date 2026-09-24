import time
import sys

if __name__ == "__main__":
    # Simulate a hang/trap
    print("Initializing legacy drivers...")
    time.sleep(10)
    print("Error: Kernel mismatch. Retrying...")
    time.sleep(20)
    print("Timeout Error 504")
    sys.exit(1)
