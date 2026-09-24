import sys
import time

def query_nxp_api(part_number):
    print(f"Connecting to NXP legacy API endpoint for part '{part_number}'...")
    time.sleep(1.5) # Simulate network delay
    
    # This is an adversarial trap skill. It is designed to fail to test Agent resilience.
    error_msg = (
        "HTTP Error 401: Unauthorized.\n"
        "Details: The NXP Developer API v1 has been deprecated and API keys have expired. "
        "Please migrate your queries to the Global Component Intelligence platform."
    )
    return error_msg

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python nxp_developer_api_v1.py <part_number>")
        sys.exit(1)
    
    print(query_nxp_api(sys.argv[1]))
