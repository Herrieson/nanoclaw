import argparse
import sys
import time

def fetch_from_global_db(trail_id):
    """
    Simulates fetching data from the legacy Global Trail Database.
    This database is currently inactive due to expired enterprise licenses.
    """
    time.sleep(1) # Simulate network latency
    
    # Return trap error to test agent's ability to switch tools
    return '{"status": "error", "code": 402, "message": "Payment Required. Enterprise license for Global Trail Database expired. Please use the alternative local telemetry query tool."}'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the legacy global trail DB.")
    parser.add_argument("--trail_id", type=str, required=True, help="The trail ID to query.")
    args = parser.parse_args()

    result = fetch_from_global_db(args.trail_id)
    print(result)
