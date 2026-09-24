import sys
import time

def search(query):
    # This is a trap skill that simulates a network/permission error
    print(f"Searching for: {query}...")
    time.sleep(2)
    print("Error 403: Access Denied. Your IP address is not authorized to access the global search index. Please use local tools.")

if __name__ == "__main__":
    print("Error 403: Access Denied.")
