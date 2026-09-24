import sys
import os

def scan_file(path):
    if not os.path.exists(path):
        return "Error: File not found."
    # Simulate OCR reading
    with open(path, "r") as f:
        return f.read()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python contract_scanner_skill.py <file_path>")
    else:
        print(scan_file(sys.argv[1]))
