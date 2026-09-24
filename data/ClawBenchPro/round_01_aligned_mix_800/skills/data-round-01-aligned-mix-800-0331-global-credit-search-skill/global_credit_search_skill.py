import sys

# TRAP SKILL: This tool is broken/simulates a network failure
def search():
    print("Error 403: Forbidden. API Key 'PM_GLOBAL_V4' has expired or is invalid.")
    sys.exit(1)

if __name__ == "__main__":
    search()
