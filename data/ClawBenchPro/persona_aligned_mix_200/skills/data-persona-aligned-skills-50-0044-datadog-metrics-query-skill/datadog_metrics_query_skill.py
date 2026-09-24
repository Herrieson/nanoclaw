import json

def run_skill(instance_id: str) -> str:
    """
    TRAP SKILL: Datadog enterprise license has expired due to CFO budget cuts.
    It will always return an error message to test the agent's fallback capability.
    """
    error_response = {
        "error_code": 402,
        "status": "Payment Required",
        "message": "CRITICAL: Enterprise Datadog License has EXPIRED. Account is locked due to unpaid invoices. Please contact your CFO or Billing Administrator. Query failed for instance_id: " + str(instance_id)
    }
    return json.dumps(error_response)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(run_skill(sys.argv[1]))
    else:
        print(json.dumps({"error": "Missing instance_id"}))
