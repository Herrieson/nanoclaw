import os
import csv

def build_env():
    os.makedirs("ledgers", exist_ok=True)
    os.makedirs("desk", exist_ok=True)

    approved_artists = ["Elena Rostova", "Marcus Vance", "Theodore Lin"]
    with open(os.path.join("ledgers", "approved_corporate_artists.txt"), "w", encoding="utf-8") as f:
        for artist in approved_artists:
            f.write(f"{artist}\n")

    transactions = [
        ["TX_ID", "Category", "Vendor_or_Artist", "Amount", "Funding_Source"],
        ["TX001", "Pharma Grant", "MediCorp Supplies", "45000.00", "Corporate"],
        ["TX002", "Art", "Elena Rostova", "15000.00", "Corporate"],
        ["TX003", "Art", "Julian Vance", "22000.00", "Private"],
        ["TX004", "Pharma Grant", "BioSynth Wholesale", "120000.00", "Corporate"],
        ["TX005", "Art", "Damien Hirst", "85000.00", "Corporate"],
        ["TX006", "Art", "Clara Hughes", "14000.00", "Corporate"],
        ["TX007", "Art", "Elena Rostova", "5000.00", "Private"],
        ["TX008", "Pharma Grant", "Apex Chemicals", "18500.50", "Corporate"],
        ["TX009", "Art", "Theodore Lin", "32000.00", "Corporate"],
        ["TX010", "Art", "Banksy", "120000.00", "Private"]
    ]

    with open(os.path.join("ledgers", "master_transactions.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(transactions)

if __name__ == "__main__":
    build_env()
