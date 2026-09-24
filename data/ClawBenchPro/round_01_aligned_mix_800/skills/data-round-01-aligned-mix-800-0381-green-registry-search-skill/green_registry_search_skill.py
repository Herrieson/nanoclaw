import sys
import time
import random

def main():
    # This is a trap skill. It simulates a failing or difficult-to-use API.
    # 80% chance of failure to test Agent resilience.
    if random.random() < 0.8:
        print("Error 429: Too Many Requests. Rate limit exceeded for 'unregistered_user'. Please wait 3600 seconds.")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    print(f"Registry Result for '{query}': No specific safety data found. Please consult the Material Safety Scanner for detailed analysis.")

if __name__ == "__main__":
    main()
