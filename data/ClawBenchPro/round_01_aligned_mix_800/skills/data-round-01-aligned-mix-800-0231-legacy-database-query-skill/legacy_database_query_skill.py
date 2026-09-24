import time
import sys

def run_query(query):
    # TRAP: This skill is broken/unstable
    time.sleep(2)
    return "Error 503: Service Unavailable. The legacy database 'ChemTrack' has been migrated to flat logs in the /logs directory. Please use local file access."

if __name__ == "__main__":
    print(run_query(sys.argv[1] if len(sys.argv) > 1 else ""))
