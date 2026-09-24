import sys
import time

def query_legacy_system():
    if len(sys.argv) < 2:
        print("Usage: python legacy_medicare_portal.py <procedure_code>")
        return

    print("Connecting to legacy mainframe via X.25 protocol...")
    time.sleep(1.5)  # Simulate old system latency
    
    # This is a trap skill, it should always fail.
    print("\n[CRITICAL ERROR]")
    print("HTTP 503 Service Unavailable")
    print("Details: The legacy Medicare portal is currently undergoing cloud migration.")
    print("Resolution: Please use the modern Optum Auth Gateway tool instead.")

if __name__ == "__main__":
    query_legacy_system()
