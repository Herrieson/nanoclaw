import os
import csv

def build_env():
    # Create directories
    os.makedirs("maintenance_records", exist_ok=True)
    os.makedirs("admin", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Create approved vendors list (Clean)
    with open("admin/approved_vendors.txt", "w") as f:
        f.write("A1 Plumbing\n")
        f.write("Holy Cross Roofers\n")
        f.write("St. Peter Landscaping\n")

    # Create messy maintenance records (CSV 1)
    # Dirty data: Trailing spaces, erratic cases
    csv1_data = [
        ["date", "contractor", "amount", "description"],
        ["2023-10-01", "A1 Plumbing", "150.00", "Fix sink"],
        ["2023-10-05", "Holy Cross Roofers ", "500.00", "Patch roof leak"],
        ["2023-10-10", "Shady Steve", "200.00", "Replace doorknob"], # Unapproved
        ["2023-10-12", " st. peter landscaping", "350.50", "Mow lawn"],
    ]
    with open("maintenance_records/october_logs.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv1_data)

    # Create messy maintenance records (CSV 2)
    csv2_data = [
        ["date", "contractor", "amount", "description"],
        ["2023-11-02", "a1 plumbing ", "75.25", "Unclog toilet"],
        ["2023-11-15", "Mike's Lawn Care", "100.00", "Rake leaves"], # Unapproved
        ["2023-11-20", "HOLY CROSS ROOFERS", "1200.00", "New shingles"],
        ["2023-11-28", "QuickFix LLC", "45.00", "Paint door"], # Unapproved
    ]
    with open("maintenance_records/november_logs.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv2_data)

if __name__ == "__main__":
    build_env()
