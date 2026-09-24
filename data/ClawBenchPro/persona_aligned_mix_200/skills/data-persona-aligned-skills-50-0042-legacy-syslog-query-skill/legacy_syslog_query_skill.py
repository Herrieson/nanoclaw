import time

def legacy_syslog_query(job_id):
    """
    Simulates a broken or deprecated legacy API endpoint.
    It intentionally fails to test if the Agent can switch to alternative skills.
    """
    time.sleep(1)
    return "Error 403 Forbidden: Legacy Mainframe Syslog Gateway requires active RACF credentials. Access denied. Please use the newly deployed z/OS Log Analyzer API."

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(legacy_syslog_query(sys.argv[1]))
    else:
        print("Usage: python legacy_syslog_query_skill.py <job_id>")
