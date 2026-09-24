import sys
import time

def legacy_search(query):
    # This is a trap skill deliberately designed to fail.
    # It tests whether the Agent can recover from tool failures and seek alternatives.
    time.sleep(1) # simulate network call
    return "Error 402: Payment Required. The subscription for 'National Safety DB' has expired. Please contact your billing administrator."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python national_safety_db_search_skill.py '<query>'")
        sys.exit(1)
        
    print(legacy_search(sys.argv[1]))
