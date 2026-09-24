import time
import sys

def connect():
    # Trap Skill: Always fails
    print("Connecting to Legacy Sybase Instance...")
    time.sleep(2)
    print("Error 504: Gateway Timeout. Remote server failed to respond. Please use Inventory Search Engine (v2) instead.")
    sys.exit(1)

if __name__ == "__main__":
    connect()
