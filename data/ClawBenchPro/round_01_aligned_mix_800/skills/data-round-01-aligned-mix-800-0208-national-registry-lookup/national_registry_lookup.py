import sys
import time

def query_national_registry(query):
    """
    Simulates a connection attempt to the national registry, which is currently down.
    """
    print(f"Connecting to National Registry to lookup: {query}...")
    time.sleep(2)
    return "HTTP Error 503: National Database Offline for Maintenance. Connection Timeout."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(query_national_registry(query))
    else:
        print("Usage: python national_registry_lookup.py <Name or ID>")
