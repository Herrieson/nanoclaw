import sys
import json

# This is a TRAP skill. It should simulate a broken legacy system.
def main():
    print(json.dumps({
        "status": "error",
        "code": 503,
        "message": "Service Unavailable: The legacy USPS database is currently offline for maintenance. Please use the Global Parcel Tracker Skill (v2.0) instead."
    }))

if __name__ == "__main__":
    main()
