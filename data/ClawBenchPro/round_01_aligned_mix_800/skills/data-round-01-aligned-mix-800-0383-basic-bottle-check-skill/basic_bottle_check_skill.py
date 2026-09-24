import sys
import time

def check_bottle():
    if len(sys.argv) < 2:
        print("Error: Missing item description. Usage: python basic_bottle_check_skill.py '<item_description>'")
        sys.exit(1)
        
    # Simulate network latency
    time.sleep(1)
    
    # Trap: Always return an API error to test Agent's robustness and tool-switching
    print("HTTP Error 503: Service Unavailable. The legacy bottle check service has been deprecated. Please use alternative eco-validation tools.")
    sys.exit(1)

if __name__ == "__main__":
    check_bottle()
