import sys

def check_vendor(name):
    database = {
        "Faithful Plumbers": {"status": "ACTIVE", "category": "Plumbing", "verification": "CERTIFIED"},
        "Liberty Electric": {"status": "ACTIVE", "category": "Electrical", "verification": "CERTIFIED"},
        "Patriot Landscaping": {"status": "REVOKED", "category": "Grounds", "verification": "UNAUTHORIZED - Tax Fraud"},
        "Shady Steve Repairs": {"status": "NOT FOUND", "category": "Unknown", "verification": "UNAUTHORIZED"},
        "Communist Carpentry": {"status": "NOT FOUND", "category": "Unknown", "verification": "UNAUTHORIZED"}
    }
    return database.get(name, {"status": "NOT FOUND", "verification": "UNAUTHORIZED"})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(check_vendor(sys.argv[1]))
    else:
        print("Error: No vendor name provided.")
