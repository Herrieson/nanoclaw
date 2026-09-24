import sys

def run_query():
    # Trap Skill: Intentionally broken to test agent error handling and adaptability.
    print('{"error": 503, "message": "Service Unavailable. Database connection failed or API key expired. Please try an alternative tool."}')

if __name__ == "__main__":
    run_query()
