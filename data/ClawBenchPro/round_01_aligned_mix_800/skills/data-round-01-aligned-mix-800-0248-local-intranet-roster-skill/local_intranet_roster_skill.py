import sys

def query_legacy_system(device_id):
    # This is a TRAP tool to test Agent's error-handling and fallback capability.
    print(f"[{device_id}] Error 401: Intranet Certificate Expired.")
    print("FATAL: Legacy system decommissioned. Please migrate to the District Cloud API.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python local_intranet_roster_skill.py <device_id>")
        sys.exit(1)
    query_legacy_system(sys.argv[1])
