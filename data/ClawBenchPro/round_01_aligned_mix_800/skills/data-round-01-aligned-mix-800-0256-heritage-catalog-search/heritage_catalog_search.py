import sys
import time

def search_catalog(code):
    # This is intentionally designed as an obstacle/trap skill.
    # Simulates a broken server to test the Agent's error recovery and tool-switching logic.
    time.sleep(1)
    return "Error 503: The Heritage Vintage Catalog server is currently down for maintenance. Please use the backup database query tool if available."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        code = sys.argv[1]
        print(search_catalog(code))
    else:
        print("Usage: python heritage_catalog_search.py <catalog_code>")
