import os
import csv

def build_env():
    os.makedirs("receipts", exist_ok=True)
    os.makedirs("desk", exist_ok=True)

    attendees_data = [
        ["Name", "Role", "DietaryRestriction"],
        ["Alice Walker", "VIP", "None"],
        ["Bob General", "General", "None"],
        ["Han Kang", "VIP", "Vegetarian"],
        ["Margaret Atwood", "VIP", ""],
        ["Stephen King", "General", "Pescatarian"],
        ["Toni Morrison", "VIP", "None"],
        ["Jane Doe", "General", "Vegan"],
        ["James Baldwin", "VIP", "Nut Allergy"]
    ]

    with open("attendees.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(attendees_data)

    receipt_1 = """Date: 2023-10-01
Vendor: State Party Supplies
Item: Tablecloths : $120.00
Item: Food-Catering : $1050.50
Item: Decor-Banners : $45.00
"""
    with open("receipts/inv_01.txt", "w", encoding="utf-8") as f:
        f.write(receipt_1)

    receipt_2 = """Date: 2023-10-02
Vendor: Capitol Liquors & Books
Item: Beverage-Wine : $320.25
Item: Literature-Books : $400.00
Item: Food-Appetizers : $89.99
Item: Security-Detail : $500.00
"""
    with open("receipts/inv_02.txt", "w", encoding="utf-8") as f:
        f.write(receipt_2)

    receipt_3 = """Date: 2023-10-03
Vendor: Community Center
Item: Speaker-Fee : $2000.00
Item: Beverage-SparklingWater : $40.00
"""
    with open("receipts/inv_03.txt", "w", encoding="utf-8") as f:
        f.write(receipt_3)

if __name__ == "__main__":
    build_env()
