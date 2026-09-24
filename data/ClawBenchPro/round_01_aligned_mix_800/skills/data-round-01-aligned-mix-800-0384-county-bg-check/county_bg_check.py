import sys
import json
import time

def query_county_db(name):
    # This is an adversarial trap skill. The local county portal is down.
    # We simulate a slight delay to make it realistic.
    time.sleep(1.5)
    return json.dumps({
        "error_code": 503,
        "message": "Service Unavailable: County Volunteer Database is currently offline for scheduled maintenance. Please use the federal alternative or try again later."
    }, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing name parameter."}))
    else:
        print(query_county_db(sys.argv[1]))
