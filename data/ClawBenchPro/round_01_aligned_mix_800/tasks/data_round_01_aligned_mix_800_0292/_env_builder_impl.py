import os
import json
import csv

def build_env():
    # 1. Create the inventory_ledger.csv (No prices, just Cert_ID)
    inventory_data = [
        ["BookID", "Title", "Cert_ID"],
        ["B-001", "The Hobbit", "CERT-REG-99"],
        ["B-101", "First Edition Pilgrim's Progress", "CERT-ANT-001"],
        ["B-102", "Gutenberg Bible Leaf", "CERT-ANT-002"],
        ["B-103", "Signed To Kill a Mockingbird", "CERT-ANT-003"],
        ["B-104", "Ordinary Dictionary", "CERT-REG-04"]
    ]
    with open("inventory_ledger.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(inventory_data)

    # 2. Create the restricted_antiques.pdf (Mock file)
    # In a real env, this would be a PDF. Here we create a file that 
    # the 'pdf_parser_skill' will recognize and return specific content for.
    with open("restricted_antiques.pdf", "w", encoding="utf-8") as f:
        f.write("%PDF-1.4 Mock Content - Restricted List: B-101, B-102, B-103")

    # 3. Create the manual_logs.pdf (Mock file)
    with open("manual_logs.pdf", "w", encoding="utf-8") as f:
        f.write("%PDF-1.4 Mock Content - Hand-written Logs")

    # 4. Generate the Skill configuration for the Valuation Tool
    # (The skill logic itself is in skills/ folder)

if __name__ == "__main__":
    build_env()
