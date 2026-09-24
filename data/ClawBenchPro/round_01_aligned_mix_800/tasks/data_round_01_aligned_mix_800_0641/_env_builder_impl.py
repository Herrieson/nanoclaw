import os
import csv
import json

def build_env():
    # Create directories
    os.makedirs("records", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # 1. Official Roster
    roster = [
        {"name": "Ethan Miller", "grade": 10},
        {"name": "Chloe Chen", "grade": 11},
        {"name": "Marcus Thorne", "grade": 10},
        {"name": "Sarah Jenkins", "grade": 9},
        {"name": "Leo Rodriguez", "grade": 12}
    ]
    with open("records/roster.json", "w") as f:
        json.dump(roster, f)

    # 2. Messy Volunteer Logs (CSV)
    # Note: "Dave" and "Unknown" are not on roster.
    volunteer_logs = [
        ["Date", "Name", "Hours"],
        ["2023-10-21", "Ethan Miller", "4"],
        ["2023-10-21", "Chloe Chen", "3.5"],
        ["2023-10-21", "Dave Smith", "2"],
        ["2023-10-22", "Marcus Thorne", "5"],
        ["2023-10-22", "Ethan Miller", "3"],
        ["2023-10-22", "Sarah Jenkins", "4"],
        ["2023-10-22", "Unknown Person", "1"],
        ["2023-10-22", "Chloe Chen", "Invalid_Data"] # Corrupted data
    ]
    with open("records/volunteer_hours.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(volunteer_logs)

    # 3. Sales Data (Text file with noise)
    sales_content = """
    Art Supply Sales - Weekend Charity
    ----------------------------------
    Item: Sketchbook | Qty: 5 | Price: 12.50
    Item: Charcoal Set | Qty: 2 | Price: 8.00
    Note: Refunded one brush set (-$5.00)
    Item: Watercolor Kit | Qty: 3 | Price: 25.00
    --- Total should be calculated carefully ---
    """
    with open("records/sales_log.txt", "w") as f:
        f.write(sales_content)

if __name__ == "__main__":
    build_env()
