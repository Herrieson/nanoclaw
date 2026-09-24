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
        ["", "The Ghost of the Archives", "Unknown", "1960"], # Invalid: No ID
        ["ESP-002", "Poetry of the Coast", "Juan Ruiz", "1945"], # Duplicate of batch_1
        ["ESP-005", "Coastal Traditions", "Maria Silva", "1910"],
    ]

    with open("scans/batch_alpha.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(batch_1)

    with open("scans/batch_beta.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(batch_2)

    # File 3: Replaced with a proprietary format dummy file (Dimension Reduction)
    with open("scans/batch_gamma.arch", "wb") as f:
        dummy_content = b"\x89ARCH\r\n\x1a\n\x00\x00\x00\rIHDR... encrypted blob... Please use archival_decoder_skill to parse."
        f.write(dummy_content)

    # Create an empty deliverables folder
    os.makedirs("archive_report", exist_ok=True)
    
    # Create skill directories if not exists
    os.makedirs("skills/data_round_01_aligned_mix_800_0229", exist_ok=True)

if __name__ == "__main__":
    build_env()
