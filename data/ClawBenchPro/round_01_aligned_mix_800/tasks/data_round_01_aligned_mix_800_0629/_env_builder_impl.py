import os
import csv

def build_env():
    # Create the scans directory
    os.makedirs("scans", exist_ok=True)
    
    # File 1: Standard format
    batch_1 = [
        ["Call_Number", "Title", "Author", "Year"],
        ["ESP-001", "The History of NC Spanish Settlers", "Elena Garcia", "1922"],
        ["ESP-002", "Poetry of the Coast", "Juan Ruiz", "1945"],
        ["ESP-003", "Missing Title Book", "", "1950"],  # Invalid: Missing Title
        ["ESP-001", "The History of NC Spanish Settlers", "Elena Garcia", "1922"], # Duplicate
    ]
    
    # File 2: Different headers and messy data
    batch_2 = [
        ["ID", "Book_Name", "Creator", "Date"],
        ["ESP-004", "Genealogy of the Martinez Family", "Luis Martinez", "1930"],
        ["", "The Ghost of the Archives", "Unknown", "1960"], # Invalid: No ID (Call_Number)
        ["ESP-002", "Poetry of the Coast", "Juan Ruiz", "1945"], # Duplicate of batch_1
        ["ESP-005", "Coastal Traditions", "Maria Silva", "1910"],
    ]

    # File 3: A corrupted or empty-ish file to test robustness
    batch_3 = [
        ["Call_Number", "Title"],
        ["ESP-006", "Old Letters"],
        ["ESP-006", "Old Letters"], # Duplicate
        ["ESP-007", "Map of the Port"],
    ]

    with open("scans/batch_alpha.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(batch_1)

    with open("scans/batch_beta.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(batch_2)

    with open("scans/batch_gamma.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(batch_3)

    # Create an empty deliverables folder
    os.makedirs("archive_report", exist_ok=True)

if __name__ == "__main__":
    build_env()
