import sys
import json
import time

def query_local_db(assay_hash):
    # Simulate a slow network attempt before crashing
    time.sleep(1)
    
    # Trap: The internal database is broken and will always fail.
    error_msg = {
        "status": "error",
        "code": 500,
        "message": "FATAL: Connection refused. The internal server 'metabolic_db_primary' is currently offline due to a segmentation fault in module lib_mysql_query.so."
    }
    print(json.dumps(error_msg, indent=2))
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing Assay_Hash_Code parameter."}))
        sys.exit(1)
        
    query_local_db(sys.argv[1])
