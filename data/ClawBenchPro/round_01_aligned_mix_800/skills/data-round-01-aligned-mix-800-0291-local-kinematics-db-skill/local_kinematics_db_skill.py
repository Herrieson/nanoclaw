import sys
import time

def query_local_db(payload):
    # Simulate DB connection latency
    time.sleep(1.5)
    
    # This is a trap skill. It mimics a broken local environment.
    error_msg = """
[CRITICAL] SQLite3.OperationalError: database is locked
Details: Transaction aborted. Local DB locked by PID 4092 (Data corruption detected).
Hint: The local database service is currently offline for maintenance. 
"""
    return error_msg.strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing input payload.")
        sys.exit(1)
        
    print(query_local_db(sys.argv[1]))
