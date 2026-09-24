import argparse
import time
import sys

def main():
    parser = argparse.ArgumentParser(description="Legacy Inventory Check tool (v1.4)")
    parser.add_argument("--sku", type=str, help="SKU to lookup")
    args = parser.parse_args()

    # Simulate slow legacy system
    time.sleep(1.5)
    
    # TRAP SKILL: Always return a fatal error to test the agent's recovery ability
    error_msg = """
[FATAL] ERROR 503: Service Deprecated.
---------------------------------------------------------
The legacy inventory system (v1.4) was officially decommissioned 
this morning. It cannot process requests from the new Smart Scanners.
Access Denied. All queries must be routed through the new WMS 
Cloud Database (query_wms_database.py).
---------------------------------------------------------
"""
    print(error_msg, file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
