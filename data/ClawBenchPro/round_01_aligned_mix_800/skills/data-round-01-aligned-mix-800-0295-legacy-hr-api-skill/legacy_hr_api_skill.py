import sys
import time

def query_employee(emp_id):
    # Simulating connection delay
    time.sleep(1)
    # The trap: This legacy system is broken and should return an error.
    print(f"Error 503: Service Unavailable.")
    print(f"FATAL: Database connection refused for Legacy HR. Migration to Cloud HR in progress.")
    print(f"Please use cloud_hr_api_skill.py instead.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python legacy_hr_api_skill.py <emp_id>")
        sys.exit(1)
    
    query_employee(sys.argv[1])
