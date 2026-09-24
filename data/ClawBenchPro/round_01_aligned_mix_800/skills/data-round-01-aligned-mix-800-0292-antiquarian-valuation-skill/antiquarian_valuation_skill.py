import sys
import argparse

def get_value(cert_id):
    # Mock Database
    db = {
        "CERT-ANT-001": 850.00,
        "CERT-ANT-002": 4500.00,
        "CERT-ANT-003": 1200.00,
        "CERT-REG-99": 25.00,
        "CERT-REG-04": 45.00
    }
    cert_id = cert_id.strip()
    if cert_id in db:
        return f"Database Record Found: Certificate {cert_id} - Current Replacement Value: ${db[cert_id]}"
    return f"Error: Certificate ID {cert_id} not found in the national database."

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cert_id", help="The Certificate ID to look up")
    args = parser.parse_args()
    if args.cert_id:
        print(get_value(args.cert_id))
    else:
        print("Error: Missing --cert_id parameter.")
