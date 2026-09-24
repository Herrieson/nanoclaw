import time
import argparse

def main():
    parser = argparse.ArgumentParser(description="Legacy Clinical Safety Checker")
    parser.add_argument("--drug", required=True, help="Name of the medication")
    parser.add_argument("--dose", required=True, help="Dosage amount (e.g. 200)")
    args = parser.parse_args()

    # Simulating a network hang then failure
    time.sleep(2)
    print("Error 503: Clinic Database Connection Timeout.")
    print("FATAL: The legacy database is currently undergoing migration. Please use the v2 API tool.")

if __name__ == "__main__":
    main()
