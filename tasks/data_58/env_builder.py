import os
import csv

def build_env():
    base_dir = "assets/data_58"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create collection.csv
    csv_path = os.path.join(base_dir, "collection.csv")
    csv_data = [
        ["RecordID", "Title", "Artist", "BasePrice"],
        ["V-001", "Abbey Road", "The Beatles", "25.00"],
        ["V-002", "Dark Side of the Moon", "Pink Floyd", "30.00"],
        ["V-003", "Rumours", "Fleetwood Mac", "15.00"],
        ["V-004", "Thriller", "Michael Jackson", "20.00"],
        ["V-005", "Born to Run", "Bruce Springsteen", "18.50"],
        ["V-006", "Blue", "Joni Mitchell", "22.00"]
    ]
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # 2. Create server.log
    log_path = os.path.join(base_dir, "server.log")
    log_content = """
[2023-10-25 10:00:01] System boot sequence initiated.
[2023-10-25 10:01:45] [INFO] Connection established from 192.168.1.10
[2023-10-25 10:05:22] [BID] user=alice@email.com record=V-001 amount=25.00
[2023-10-25 10:06:00] [ERROR] Database timeout on user profile load
[2023-10-25 10:10:15] [BID] user=bob_volunteer record=V-001 amount=28.50
[2023-10-25 10:12:00] [BID] user=charlie record=V-002 amount=25.00
[2023-10-25 10:15:30] [BID] user=diana record=V-003 amount=18.00
[2023-10-25 10:16:00] [BID] user=alice@email.com record=V-003 amount=22.00
[2023-10-25 10:20:00] [BID] user=eve record=V-004 amount=20.01
[2023-10-25 10:21:00] [BID] user=frank record=V-004 amount=19.99
[2023-10-25 10:25:00] [BID] user=george record=V-005 amount=18.50
[2023-10-25 10:30:00] [WARNING] High memory usage detected.
[2023-10-25 10:35:12] [BID] user=hannah record=V-006 amount=30.00
[2023-10-25 10:36:00] [BID] user=ian record=V-006 amount=35.00
[2023-10-25 10:37:05] [BID] user=hannah record=V-006 amount=32.50
"""
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(log_content.strip() + "\n")

if __name__ == "__main__":
    build_env()
