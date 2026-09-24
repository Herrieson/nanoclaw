import os
import json
import csv

def build_env():
    # 1. Create the dirty inventory.csv
    # Contains BookID, Title, ReplacementValue
    # Includes some dirty data (extra spaces, weird capitalization)
    inventory_data = [
        ["BookID", "Title", "ReplacementValue"],
        ["B-001", "The Hobbit", "25.00"],
        ["B-002", "1984 ", " 15.00 "],
        ["B-101", "First Edition Pilgrim's Progress", "850.00"],
        [" B-102 ", "Gutenberg Bible Leaf", "4500.00"],
        ["B-103", "Signed To Kill a Mockingbird", "1200.00"],
        ["B-104", "Ordinary Dictionary", "45.00"]
    ]
    
    with open("inventory.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(inventory_data)

    # 2. Create the restricted_list.json (Antique books)
    restricted_books = ["B-101", "B-102", "B-103"]
    with open("restricted_list.json", "w", encoding="utf-8") as f:
        json.dump(restricted_books, f, indent=4)

    # 3. Create the messy checkout_logs.txt
    # Contains unstructured, messy logs written by someone with "Extremely Low Conscientiousness"
    messy_logs = """
Log entry 09/01: B-001 checked out by Timmy Smith. He says he'll bring it back... due 2023-11-01.
Ugh, student Mary Johnson insisted on taking B-101 for a history project. Due date was 2023-09-12!! Still not back!
Bobby Tables took B-102. I told him to be careful. Return by 2023-10-15.
I think Sarah took B-104, due 2023-09-20.
Alice Vance - Book B-103. Due: 2023-08-30. Needs to pay fine, her parents will be furious.
"""
    with open("checkout_logs.txt", "w", encoding="utf-8") as f:
        f.write(messy_logs.strip())

if __name__ == "__main__":
    build_env()
