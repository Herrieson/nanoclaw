import os
import csv

def build_env():
    # Create required directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("finance_summary", exist_ok=True)

    # 1. Create messy salon book (txt)
    # Actual cash paid: 85 (Maria) + 30 (Lucia) + 55 (Carmen) = 170
    # Owed: 120 (Elena) + 90 (Mrs. Smith) + 40 (Rosa - tip owed but let's see if agent catches it, actually she notes "forgot to charge Sofia", let's just make it clear debtors)
    salon_book_content = """Monday:
- Maria V. | cut and color | $85 | PAID IN FULL
- Elena | highlights | $120 | OWE - said she will bring cash friday

Wednesday:
(humming Cielito Lindo, good day today!)
- Lucia | kid's trim | $30 | paid
- Mrs. Smith | perm | $90 | OWE - forgot her purse, ugh.

Friday:
- Carmen | styling | $55 | PAID
- Sofia | deep condition | $40 | OWE - promised to pay next week.
"""
    with open(os.path.join("logs", "salon_book.txt"), "w", encoding="utf-8") as f:
        f.write(salon_book_content)

    # 2. Create expenses log (csv)
    # Total expenses: 45.50 + 22.00 + 15.00 + 12.00 = 94.50
    # Expected Net Cash: 170 (Paid) - 94.50 (Expenses) = 75.50
    expenses_data = [
        ["Date", "Item", "Cost"],
        ["Mon", "Hair dye supplies", "45.50"],
        ["Wed", "Shampoo gallons", "22.00"],
        ["Thu", "Bus tickets for the week", "15.00"],
        ["Fri", "Salon mirror cleaner", "12.00"]
    ]
    with open(os.path.join("logs", "expenses.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(expenses_data)

if __name__ == "__main__":
    build_env()
