import sys
import time

def lookup(name):
    # Simulating connection delay
    time.sleep(1)
    return "Error 401: Enterprise License Expired. Authentication server at on-prem node failed. Please migrate to the new bicsi_cloud_api."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python legacy_bicsi_cert_lookup.py <volunteer_name>")
    else:
        name = " ".join(sys.argv[1:])
        print(lookup(name))
