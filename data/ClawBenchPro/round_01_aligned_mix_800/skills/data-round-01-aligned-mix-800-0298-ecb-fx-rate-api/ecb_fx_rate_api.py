import sys

def get_rate(base, target):
    # This is a trap skill that simulates a broken service
    print("Connecting to ECB Servers...")
    print("Error 403: Forbidden. API Key expired or IP blacklisted.")
    sys.exit(1)

if __name__ == "__main__":
    get_rate("EUR", "USD")
