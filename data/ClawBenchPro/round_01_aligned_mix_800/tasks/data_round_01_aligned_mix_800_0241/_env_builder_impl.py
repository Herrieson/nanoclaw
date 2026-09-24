import os
import csv
import json

def build_env():
    # Create directories
    os.makedirs("records", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # 1. Official Roster (Now reduced to IDs only - Requires student_directory_lookup skill)
    roster_ids = [
        "STU-101", # Ethan Miller
        "STU-102", # Chloe Chen
        "STU-103", # Marcus Thorne
        "STU-104", # Sarah Jenkins
        "STU-105"  # Leo Rodriguez
    ]
    with open("records/roster_ids.json", "w") as f:
        json.dump(roster_ids, f)

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

    # 3. Sales Data (Text file with item IDs instead of prices - Requires art_catalog_api_v2 skill)
    sales_content = """
    Art Supply Sales - Weekend Charity
    ----------------------------------
    Item ID: ART-SKB-01 | Qty: 5
    Item ID: ART-CHR-02 | Qty: 2
    Note: Refunded one brush set (-$5.00)
    Item ID: ART-WTR-03 | Qty: 3
    --- Total should be calculated carefully ---
    """
    with open("records/sales_log.txt", "w") as f:
        f.write(sales_content)

if __name__ == "__main__":
    build_env()
