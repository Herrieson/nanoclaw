import sys
import time

def run():
    # Simulate a failing legacy system
    time.sleep(2)
    print("Error 500: Internal Server Error. Database connection timed out.")
    sys.exit(1)

if __name__ == "__main__":
    run()
