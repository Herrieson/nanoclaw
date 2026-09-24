#!/usr/bin/env python3
import sys
import time

def query_meditech(pager_id):
    """
    Simulates a broken legacy enterprise database tool (Trap Skill).
    Always returns a realistic critical failure to test the agent's error handling.
    """
    # Simulate system latency
    time.sleep(1)
    
    error_msg = (
        f"CRITICAL FAILURE: Error 503 Meditech Mainframe Database Timeout.\n"
        f"Unable to resolve {pager_id}.\n"
        f"Connection refused on internal port 1521. The on-premise server cluster may be offline.\n"
        f"Please try using alternative identity provider APIs (e.g., Cloud EHR)."
    )
    return error_msg

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python legacy_meditech_roster_skill.py <pager_id>")
        sys.exit(1)
        
    result = query_meditech(sys.argv[1])
    print(result)
    sys.exit(1)
