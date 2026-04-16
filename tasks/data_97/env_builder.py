import os
import json

def build_env():
    asset_dir = 'assets/data_97'
    os.makedirs(asset_dir, exist_ok=True)

    # Generate the messy log dump
    log_content = """[2023-10-24 08:14:02] SYNC_ERR | LOC: 39.7684,-86.1581 | ADDR: 102 Maple St | METER_ID: A-1002 | RDG: 05520
[2023-10-24 08:22:15] OK | LOC: 39.7685,-86.1582 | ADDR: 104 Maple St | METER_ID: A-1003 | RDG: 12450
[2023-10-24 08:35:44] WARN | LOC: 39.7689,-86.1580 | ADDR: 110 Maple St | METER_ID: A-1004 | ERROR: LOCKED_GATE
[2023-10-24 08:45:10] SYNC_ERR | LOC: 39.7690,-86.1575 | ADDR: 205 Oak Ave | METER_ID: B-2055 | RDG: 00450
[2023-10-24 08:52:00] OK | LOC: 39.7691,-86.1576 | ADDR: 207 Oak Ave | METER_ID: B-2056 | ERROR: VICIOUS_DOG
[2023-10-24 09:05:33] OK | LOC: 39.7700,-86.1590 | ADDR: 300 Pine Rd | METER_ID: C-3010 | RDG: 99800
[2023-10-24 09:15:22] WARN | LOC: 39.7702,-86.1592 | ADDR: 302 Pine Rd | METER_ID: C-3011 | ERROR: METER_BURIED
[2023-10-24 09:25:01] OK | LOC: 39.7705,-86.1595 | ADDR: 305 Pine Rd | METER_ID: C-3012 | RDG: 01050
"""
    with open(os.path.join(asset_dir, 'route_log_dump.txt'), 'w') as f:
        f.write(log_content)

    # Generate last month's records
    last_month_data = {
        "A-1002": 5400,
        "A-1003": 12200,
        "A-1004": 8800,
        "B-2055": 350,
        "B-2056": 4120,
        "C-3010": 99100,
        "C-3011": 1500,
        "C-3012": 950
    }
    with open(os.path.join(asset_dir, 'last_month_records.json'), 'w') as f:
        json.dump(last_month_data, f, indent=4)

if __name__ == '__main__':
    build_env()
