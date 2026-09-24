import sys
import time

def query_legacy(employee_id):
    # Simulate network latency
    time.sleep(1.5)
    print("Connecting to Legacy PA HR Portal Database...")
    time.sleep(0.5)
    print("CRITICAL ERROR: 503 Service Unavailable.")
    print("DETAILS: Billing account for Legacy Enterprise Portal has been suspended. Please migrate all operations to the 'pa_hr_directory_nextgen' system.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 pa_hr_directory_legacy.py <PA_ID>")
        sys.exit(1)
    query_legacy(sys.argv[1])
