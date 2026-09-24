import sys
import time

def query_vip(name):
    print("Connecting to Legacy SQL Server database...")
    time.sleep(1) # simulate connection latency
    return "Error 504: Database connection timeout. \nThe Legacy System has been decommissioned. Please use the modern 'nextgen_crm_api' for all customer lookups."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python legacy_vip_query.py '<Customer_Name>'")
        sys.exit(1)
        
    print(query_vip(sys.argv[1]))
