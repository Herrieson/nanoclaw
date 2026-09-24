import os
import csv
import random

os.makedirs("student_logs", exist_ok=True)
os.makedirs("reports", exist_ok=True)

data = [
    {"student": "Alice", "minutes": 45, "status": "VALID"},
    {"student": "Bob", "minutes": 30, "status": "VALID"},
    {"student": "Charlie", "minutes": 120, "status": "VALID"},
    {"student": "David", "minutes": 15, "status": "VALID"},
    {"student": "Alice", "minutes": 999, "status": "GLITCH"},
    {"student": "Bob", "minutes": 20, "status": "VALID"},
    {"student": "Eve", "minutes": 50, "status": "VALID"},
    {"student": "David", "minutes": 60, "status": "VALID"},
    {"student": "Charlie", "minutes": 0, "status": "SYNC_ERROR"},
    {"student": "Alice", "minutes": 65, "status": "VALID"},
    {"student": "Eve", "minutes": 55, "status": "VALID"},
    {"student": "Frank", "minutes": 10, "status": "VALID"},
    {"student": "Frank", "minutes": 80, "status": "VALID"}
]

random.shuffle(data)

with open("student_logs/read_o_tron_export.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["student", "minutes", "status"])
    writer.writeheader()
    for row in data:
        writer.writerow(row)
