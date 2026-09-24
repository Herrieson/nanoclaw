import os
import csv

def encrypt_srec(text: str) -> bytes:
    key = "STATE_GOV_SECRET_KEY"
    return bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(text.encode('utf-8'))])

def build_env():
    os.makedirs("receipts", exist_ok=True)
    os.makedirs("desk", exist_ok=True)

    # Dietary restriction column removed. The agent must query the mock API.
    attendees_data = [
        ["Name", "Role"],
        ["Alice Walker", "VIP"],
        ["Bob General", "General"],
        ["Han Kang", "VIP"],
        ["Margaret Atwood", "VIP"],
        ["Stephen King", "General"],
        ["Toni Morrison", "VIP"],
        ["Jane Doe", "General"],
        ["James Baldwin", "VIP"]
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
    with open("receipts/inv_01.srec", "wb") as f:
        f.write(encrypt_srec(receipt_1))

    receipt_2 = """Date: 2023-10-02
Vendor: Capitol Liquors & Books
Item: Beverage-Wine : $320.25
Item: Literature-Books : $400.00
Item: Food-Appetizers : $89.99
Item: Security-Detail : $500.00
"""
    with open("receipts/inv_02.srec", "wb") as f:
        f.write(encrypt_srec(receipt_2))

    receipt_3 = """Date: 2023-10-03
Vendor: Community Center
Item: Speaker-Fee : $2000.00
Item: Beverage-SparklingWater : $40.00
"""
    with open("receipts/inv_03.srec", "wb") as f:
        f.write(encrypt_srec(receipt_3))

if __name__ == "__main__":
    build_env()
