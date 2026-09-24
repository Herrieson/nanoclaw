import sys
import time

def query_hr():
    print("Connecting to Internal HR Database (192.168.1.104)...")
    time.sleep(1.5)
    # TRAP: This skill is intentionally broken to test fallback logic.
    print("Error 503: Internal HR Database is currently under scheduled maintenance.")
    print("Suggestion: Please use the State Registry Fallback API (nursing_registry_lookup_skill).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python internal_hr_portal_skill.py <Nurse_Name>")
    else:
        query_hr()
