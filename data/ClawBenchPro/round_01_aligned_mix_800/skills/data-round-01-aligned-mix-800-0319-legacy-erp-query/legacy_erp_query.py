import sys
import time

def query_legacy_system(part_name):
    print(f"Connecting to Legacy ERP System (192.168.1.104) to look up {part_name}...")
    # Simulate loading time
    time.sleep(1.5)
    
    # TRAP: The legacy system is permanently offline/broken.
    print("ERROR 504: Gateway Timeout.")
    print("FATAL: Database connection refused. System migration in progress.")
    print("Please contact IT or use the new cloud ERP alternatives.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python legacy_erp_query.py <part_name>")
        sys.exit(1)
        
    query_legacy_system(sys.argv[1])
