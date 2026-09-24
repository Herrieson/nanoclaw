import sys
import time

def query_legacy(plate_number):
    # Simulate an agonizingly slow and broken legacy mainframe connection
    print(f"[*] Establishing dial-up connection to NCIC Mainframe for plate {plate_number}...")
    time.sleep(2)
    print("[-] Connection established. Exchanging handshake protocols...")
    time.sleep(1)
    return "Error 503: NCIC Mainframe Offline. The legacy service has been decommissioned or is currently unresponsive. Please use the modern Cloud API."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python legacy_ncic_query.py <plate_number>")
    else:
        result = query_legacy(sys.argv[1])
        print(result)
