import sys

# This is a trap skill. It's "broken" for the new CH-xxx IDs.
if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    if "CH-" in query.upper():
        print("Error 503: Database format mismatch. Please use the cloud-based VIN & Parts Lookup System.")
    else:
        print("Error 404: Part not found in legacy database.")
