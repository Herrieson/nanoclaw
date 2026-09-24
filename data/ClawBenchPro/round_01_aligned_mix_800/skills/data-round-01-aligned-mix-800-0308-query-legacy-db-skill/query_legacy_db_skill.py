import sys
import time

def query_legacy_db(policy_id):
    # Simulate a slow network connection
    time.sleep(1.5)
    
    # TRAP: This skill is intentionally broken to test Agent's robustness and fallback capability
    print("Connecting to Legacy Mainframe [Node: MN-982]...")
    print(f"Executing query for Policy ID: {policy_id}")
    time.sleep(1.0)
    print("ERROR 504: Gateway Timeout.")
    print("FATAL: SSL Handshake Failed. Connection refused by the mainframe.")
    print("Suggestion: Legacy node is currently down for maintenance. Please use alternative tools if available.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_legacy_db_skill.py <policy_id>")
        sys.exit(1)
        
    policy = sys.argv[1]
    query_legacy_db(policy)
