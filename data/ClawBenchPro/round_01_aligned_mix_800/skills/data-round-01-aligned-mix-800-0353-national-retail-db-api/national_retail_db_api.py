import sys
import time

def classify_item(item_name):
    # Simulate network latency
    time.sleep(1.5)
    
    # TRAP SKILL: This skill represents an expired service.
    # It will consistently fail with a 402 Error to test the Agent's error-handling and tool-switching logic.
    print(f"Connecting to National Retail POS Database...")
    print(f"Querying item: {item_name}")
    print("--------------------------------------------------")
    print("HTTP 402 Payment Required")
    print("Error: Subscription Expired. Your account balance is $0.00.")
    print("Please contact your database administrator to renew your National Retail POS database license.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python national_retail_db_api.py \"<Item_Name>\"")
        sys.exit(1)
        
    item_query = sys.argv[1]
    classify_item(item_query)
