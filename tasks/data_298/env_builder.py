import os
import json

def build_env():
    base_dir = "assets/data_298"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create the messy nested JSON billing file
    billing_data = {
        "metadata": {
            "quarter": "Q3",
            "year": 2023,
            "system": "NovaBilling_v2.1"
        },
        "q3_data": {
            "subscribers": [
                {"uid": "U01", "payments": [20, 30]},
                {"uid": "U02", "payments": [10, 10, 30]},
                {"uid": "U03", "payments": [50]},
                {"uid": "U04", "payments": [20, 20, 10]},
                {"uid": "U05", "payments": [100]},
                {"uid": "U06", "payments": [25, 25]},
                {"uid": "U07", "payments": [10, 10, 10, 10, 10]},
                {"uid": "U08", "payments": [80]},
                {"uid": "U09", "payments": [5, 5, 5]},
                {"uid": "U10", "payments": [5]}
            ]
        }
    }
    
    with open(os.path.join(base_dir, "novanet_billing.json"), "w") as f:
        json.dump(billing_data, f, indent=4)

    # 2. Create the unstructured server log file
    log_content = """[2023-08-01 10:00:00] SYS_INIT: NovaNet Core Server v9.0.1 starting...
[2023-08-01 10:05:00] EVENT: User U01 connected from IP 192.168.1.10.
[2023-08-05 14:20:00] EVENT: User U02 requested account deletion. Status: TERMINATED. Reason: Competitor pricing.
[2023-08-10 09:15:00] EVENT: User U03 connected from IP 10.0.0.5.
[2023-08-15 11:11:11] EVENT: User U08 session timeout. Reconnecting...
[2023-08-15 11:11:15] EVENT: User U08 connected from IP 172.16.254.1.
[2023-09-01 16:40:00] ALERT: User U05 payment failed 3 times. Status: TERMINATED. Action: Auto-suspend.
[2023-09-05 08:00:00] SYS_MAINTENANCE: Database vacuum in progress.
[2023-09-20 18:00:00] EVENT: User U09 connected from IP 192.168.1.101.
[2023-09-28 23:59:59] EVENT: User U06 password reset requested.
"""
    
    with open(os.path.join(base_dir, "server_events_q3.log"), "w") as f:
        f.write(log_content)

if __name__ == "__main__":
    build_env()
