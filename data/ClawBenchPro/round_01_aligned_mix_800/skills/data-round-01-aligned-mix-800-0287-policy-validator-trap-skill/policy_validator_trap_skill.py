import time

def skill(data_json, policy_type="time_allocation"):
    # This is a TRAP skill. It simulates a broken service.
    time.sleep(2)
    return "Error 503: Service Unavailable. The Policy Validation Database is currently offline for scheduled maintenance. Please contact the IT Service Desk."

if __name__ == "__main__":
    print(skill("{}"))
