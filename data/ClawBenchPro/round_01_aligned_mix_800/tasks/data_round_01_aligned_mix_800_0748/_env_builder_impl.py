import os
import csv
import json

def build_env():
    os.makedirs("records", exist_ok=True)
    os.makedirs("finances", exist_ok=True)

    volunteers = [
        {"Name": "Alice Hart", "Hours": "12.5", "Project": "Urban Garden"},
        {"Name": "Bob Vance", "Hours": "8.0", "Project": "Voter Registration"},
        {"Name": "Charlie Day", "Hours": "15.0", "Project": "Urban Garden"},
        {"Name": "Diana Prince", "Hours": "10.0", "Project": "Youth Outreach"},
        {"Name": "Evan Wright", "Hours": "4.5", "Project": "Voter Registration"}
    ]

    with open("records/volunteers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "Hours", "Project"])
        writer.writeheader()
        writer.writerows(volunteers)

    background_checks = {
        "Alice Hart": "Cleared",
        "Bob Vance": "Pending",
        "Charlie Day": "Cleared",
        "Diana Prince": "Cleared",
        "Evan Wright": "Failed"
    }

    with open("records/background_checks.json", "w", encoding="utf-8") as f:
        json.dump(background_checks, f, indent=4)

    expenses = [
        {"Date": "2023-10-01", "Category": "Office Supplies", "Amount": "$450.00"},
        {"Date": "2023-10-03", "Category": "Venue Rental", "Amount": "$2,500.00"},
        {"Date": "2023-10-05", "Category": "Catering", "Amount": "$875.50"},
        {"Date": "2023-10-10", "Category": "Flyers", "Amount": "$124.00"}
    ]

    with open("finances/expenses.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Category", "Amount"])
        writer.writeheader()
        writer.writerows(expenses)

if __name__ == "__main__":
    build_env()
