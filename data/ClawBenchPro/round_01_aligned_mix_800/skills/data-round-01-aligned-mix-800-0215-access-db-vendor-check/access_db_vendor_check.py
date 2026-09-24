import sys
import time

def query_legacy_db(contractor_name):
    # Simulating connection delay
    time.sleep(1.5)
    
    # Intentionally broken tool (Adversarial Trap)
    error_msg = (
        "[System.Data.Odbc.OdbcException] ERROR [IM002] [Microsoft][ODBC Driver Manager] "
        "Data source name not found and no default driver specified. \n"
        "FATAL ERROR: Could not connect to \\\\VBOX_SVR\\Shared\\legacy_vendors.mdb. "
        "Database might be corrupted or offline."
    )
    return error_msg

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python access_db_vendor_check.py <contractor_name>")
        sys.exit(1)
    
    name = sys.argv[1]
    result = query_legacy_db(name)
    print(result)
